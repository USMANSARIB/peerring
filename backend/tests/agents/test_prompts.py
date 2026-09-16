"""
Unit tests for Socratic Tutor and Peer Prompt Engines.

Verifies:
1. Bob prompt generation, Assistance Ladder descriptions, and Pólya deliberation inclusion.
2. Alice prompt generation, error injection toggling, and arithmetic taxonomy boundaries.
3. Charlie prompt generation, error injection toggling, and conceptual taxonomy boundaries.
4. Peer snapshot and multi-party name mention instructions across all prompts.
"""

import pytest
from app.state.pydantic_state import PeerRingState, DialogueMessage, MessageRole
from app.prompts import (
    BOB_SYSTEM_PROMPT,
    ALICE_SYSTEM_PROMPT,
    CHARLIE_SYSTEM_PROMPT,
    ASSISTANCE_LADDER_DESCRIPTIONS,
    build_bob_prompt,
    build_alice_prompt,
    build_charlie_prompt,
    format_peer_snapshot,
    format_conversation_history,
    format_curriculum_context,
)


@pytest.fixture
def sample_state():
    state = PeerRingState(session_id="prompt-test-session")
    state.messages.append(DialogueMessage(role=MessageRole.USER, content="Hey Alice, can you help with this?"))
    state.messages.append(DialogueMessage(role=MessageRole.AGENT, agent_id="alice-peer", content="Sure! -2(x - 3) = -2x - 6"))
    state.messages.append(DialogueMessage(role=MessageRole.AGENT, agent_id="charlie-peer", content="Alice, check your signs."))
    return state


def test_bob_prompt_contract(sample_state):
    prompt = build_bob_prompt(sample_state, latest_user_input="Bob, is Charlie right?")
    
    assert "You are Bob" in prompt
    assert "<think>" in prompt
    assert "Pólya" in prompt or "Polya" in prompt or "1. Understand the Problem:" in prompt
    assert "HANDLING WHEN THE STUDENT MENTIONS YOU, ALICE, OR CHARLIE BY NAME:" in prompt
    assert "ZERO DIRECT ANSWER DISCLOSURE" in prompt
    assert "Recent Study Pod Dialogue:" in prompt
    assert "Alice most recently said:" in prompt
    assert "Charlie most recently said:" in prompt
    assert "Level" in prompt


def test_alice_prompt_contract(sample_state):
    # Slip mode
    slip_prompt = build_alice_prompt(sample_state, latest_user_input="Alice, what did you get?", inject_error=True)
    assert "You are Alice" in prompt_check(slip_prompt)
    assert "ARITHMETIC CALCULATION SLIP" in slip_prompt
    assert "CARDINAL RULES" in slip_prompt
    assert "ZERO CONCEPTUAL ERRORS" in slip_prompt
    assert "HANDLING WHEN THE STUDENT MENTIONS YOU, BOB, OR CHARLIE BY NAME:" in slip_prompt

    # Clean mode
    clean_prompt = build_alice_prompt(sample_state, latest_user_input="Alice, what did you get?", inject_error=False)
    assert "CLEAN, accurate step" in clean_prompt
    assert "100% accurate" in clean_prompt


def test_charlie_prompt_contract(sample_state):
    # Trap mode
    trap_prompt = build_charlie_prompt(sample_state, latest_user_input="Charlie, any shortcuts?", inject_error=True)
    assert "You are Charlie" in prompt_check(trap_prompt)
    assert "CONCEPTUAL SHORTCUT" in trap_prompt
    assert "CARDINAL RULES" in trap_prompt
    assert "FLAWLESS ARITHMETIC GUARANTEE" in trap_prompt
    assert "HANDLING WHEN THE STUDENT MENTIONS YOU, BOB, OR ALICE BY NAME:" in trap_prompt

    # Clean mode
    clean_prompt = build_charlie_prompt(sample_state, latest_user_input="Charlie, any shortcuts?", inject_error=False)
    assert "COMPLETELY VALID algebraic simplification" in clean_prompt
    assert "100% mathematically sound" in clean_prompt


def test_peer_snapshot_formatting(sample_state):
    snapshot = format_peer_snapshot(sample_state)
    assert "Alice most recently said:" in snapshot
    assert "Charlie most recently said:" in snapshot


def prompt_check(p: str) -> str:
    return p
