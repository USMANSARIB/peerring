"""
Prompts package for PeerRing agents.

Provides canonical system prompts and builder functions for:
- Bob (Socratic Tutor)
- Alice (Arithmetic Peer)
- Charlie (Conceptual Peer)
- Peer Taxonomy and Error Isolation
"""

from app.prompts.bob_socratic import (
    BOB_SYSTEM_PROMPT,
    ASSISTANCE_LADDER_DESCRIPTIONS,
    build_bob_prompt,
    format_conversation_history,
    format_curriculum_context,
    format_peer_snapshot,
)
from app.prompts.peer_alice import (
    ALICE_SYSTEM_PROMPT,
    build_alice_prompt,
)
from app.prompts.peer_charlie import (
    CHARLIE_SYSTEM_PROMPT,
    build_charlie_prompt,
)
from app.prompts.peer_taxonomy import (
    ArithmeticErrorType,
    ConceptualErrorType,
    validate_error_isolation,
)

__all__ = [
    "BOB_SYSTEM_PROMPT",
    "ASSISTANCE_LADDER_DESCRIPTIONS",
    "build_bob_prompt",
    "format_conversation_history",
    "format_curriculum_context",
    "format_peer_snapshot",
    "ALICE_SYSTEM_PROMPT",
    "build_alice_prompt",
    "CHARLIE_SYSTEM_PROMPT",
    "build_charlie_prompt",
    "ArithmeticErrorType",
    "ConceptualErrorType",
    "validate_error_isolation",
]

