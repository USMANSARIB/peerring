"""
WebSocket Router for Real-time Communication
Handles WebSocket connections and turn-based message flow
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import logging
from datetime import datetime

from app.config import settings
from app.state.pydantic_state import PeerRingState, DialogueMessage, MessageRole
from app.contracts.mock_registry import mock_registry
from app.telemetry.prism_client import prism_client

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session state storage for development
session_states: Dict[str, PeerRingState] = {}


def get_or_create_session_state(session_id: str) -> PeerRingState:
    """Get existing PeerRingState or create a new session state."""
    if session_id not in session_states:
        session_states[session_id] = PeerRingState(session_id=session_id)
    return session_states[session_id]


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_locks: Set[str] = set()

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a WebSocket connection and register it."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"Session {session_id} connected")

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        self.session_locks.discard(session_id)
        logger.info(f"Session {session_id} disconnected")

    async def send_personal_message(self, message: dict, session_id: str):
        """Send a message to a specific session."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected sessions."""
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Main WebSocket endpoint for real-time communication.
    Handles turn-based message flow with MockAgentRegistry integration.
    """
    await manager.connect(websocket, session_id)
    state = get_or_create_session_state(session_id)

    # Send initial state sync upon connection
    await manager.send_personal_message(
        {
            "type": "STATE_SYNC",
            "session_id": session_id,
            "turn_count": state.turn_count,
            "policy": {
                "assistance_level": state.policy.assistance_level.current_level,
                "assistance_level_name": state.policy.assistance_level.level_names[state.policy.assistance_level.current_level - 1],
                "struggle_score": state.policy.struggle_score,
                "recovery_state": state.policy.recovery_state.value,
            },
            "messages_count": len(state.messages),
            "timestamp": datetime.utcnow().isoformat()
        },
        session_id
    )

    try:
        while True:
            # Wait for incoming message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Malformed JSON payload"},
                    session_id
                )
                continue

            # Basic message validation
            if not isinstance(message, dict) or "type" not in message:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid message format"},
                    session_id
                )
                continue

            # Handle different message types
            if message["type"] == "USER_MESSAGE":
                await handle_user_message(session_id, message)
            elif message["type"] == "PING":
                await manager.send_personal_message(
                    {"type": "PONG", "timestamp": message.get("timestamp")},
                    session_id
                )
            else:
                logger.warning(f"Unknown message type: {message.get('type')}")

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)


async def handle_user_message(session_id: str, message: dict):
    """
    Handle incoming user messages through MockAgentRegistry, PRISM telemetry ambient sessions, and state updates.
    """
    content = message.get("content", "").strip()
    if not content:
        await manager.send_personal_message(
            {"type": "error", "message": "Message content cannot be empty"},
            session_id
        )
        return

    state = get_or_create_session_state(session_id)

    # Wrap turn execution in ambient PRISM session context (Step 5)
    with prism_client.ambient_session(session_id):
        # Execute mock turn
        result = await mock_registry.run_mock_turn(state, content)

        if "error" in result:
            await manager.send_personal_message(
                {"type": "error", "message": result["error"]},
                session_id
            )
            return

        response = result["response"]
        governance = result["governance"]
        winner_id = result["winner"]

        # Record manual PRISM traces for agent turn (Step 7 - stable IDs: bob-tutor, alice-peer, charlie-peer)
        prism_client.trace_agent_turn_async(
            session_id=session_id,
            agent_id=response.agent_id,
            user_input=content,
            response_text=response.content,
            latency_ms=response.generation_time_ms or 150,
            metadata={
                "has_blackboard_patch": response.blackboard_patch is not None,
                "confidence": response.confidence,
                "struggle_score": state.policy.struggle_score,
                "assistance_level": state.policy.assistance_level.current_level,
            }
        )

        # Record manual PRISM traces for governance judges (Step 7 - stable IDs: leak-judge, help-judge)
        for jtype, verdict in governance.items():
            prism_client.trace_judge_eval_async(
                session_id=session_id,
                judge_type=jtype,
                evaluated_text=response.content,
                verdict=verdict,
                latency_ms=verdict.evaluation_time_ms or 50
            )

        governance_flags = {
            jtype: verdict.verdict for jtype, verdict in governance.items()
        }

        # Format agent response event for client
        agent_response_event = {
            "type": "AGENT_RESPONSE",
            "session_id": session_id,
            "agent_id": response.agent_id,
            "active_speaker": winner_id,
            "content": response.content,
            "think_block": response.think_block,
            "blackboard_patch": response.blackboard_patch,
            "governance_flags": governance_flags,
            "policy_state": {
                "assistance_level": state.policy.assistance_level.current_level,
                "assistance_level_name": state.policy.assistance_level.level_names[state.policy.assistance_level.current_level - 1],
                "struggle_score": state.policy.struggle_score,
                "recovery_state": state.policy.recovery_state.value
            },
            "turn_count": state.turn_count,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": response.metadata
        }

        await manager.send_personal_message(agent_response_event, session_id)