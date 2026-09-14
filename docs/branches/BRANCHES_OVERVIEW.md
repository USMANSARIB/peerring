# Spatial PeerRing — Repository Branch Topology & Documentation

This document provides a comprehensive mapping and documentation of all branches across **NAD (Foundation & Governance)**, **USM (Agent Intelligence)**, and **MUW (Spatial UI & Observability / Evaluation)**.

---

## 1. Branch Hierarchy Graph

```text
main (Production Base)
 ├── foundation/core-contracts-and-state (NAD Foundation Base)
 │    ├── foundation/redis-turn-mutex (NAD Redis Mutex & Serialization)
 │    │
 │    ├── feature/bob-socratic-tutor (USM Bob Socratic Agent)
 │    ├── feature/alice-charlie-peers (USM Alice Arithmetic & Charlie Conceptual Peers)
 │    ├── feature/pedagogical-orchestrator (USM Orchestrator Graph & Candidate Selection)
 │    ├── feature/assistance-hint-ladder (USM 6-Level Assistance Ladder)
 │    ├── feature/mastery-struggle-detection (USM Struggle Score & Mastery Engine)
 │    │    └── subfeature/mastery-struggle/recovery-state-machine (USM Recovery FSM)
 │    │
 │    ├── feature/leak-judge (NAD Solution Leak Judge)
 │    ├── feature/help-judge-rewriter (NAD Helpfulness Judge & Policy Rewriter)
 │    ├── feature/adversarial-resistance (NAD Adversarial Input Classifier)
 │    │
 │    └── feature/prism-pipeline-instrumentation (MUW PRISM SDK & Ambient Session Base)
 │         └── subfeature/prism/seven-pillar-scoring (MUW 7-Pillar Scorer & Trust Pack)
 │              └── subfeature/prism/adversarial-test-suite (MUW Adversarial Test Suite - Active HEAD)
```

---

## 2. Comprehensive Branch Reference

### A. Foundation & Core Layer (NAD)

#### 1. `main`
- **Owner**: Team Lead / Shared
- **Purpose**: Stable production branch containing project PRD, Integration Guide, Roadmap, and primary documentation.

#### 2. `foundation/core-contracts-and-state`
- **Owner**: `nad`
- **Purpose**: Core Pydantic state schema (`PeerRingState`), abstract interfaces (`BaseAgent`, `BaseJudge`), and `MockAgentRegistry` enabling parallel team development.
- **Key Files**: `backend/app/state/pydantic_state.py`, `backend/app/contracts/base_agent.py`, `backend/app/contracts/mock_registry.py`.

#### 3. `foundation/redis-turn-mutex`
- **Owner**: `nad`
- **Purpose**: Redis connection setup, turn locking (`SETNX`), state JSON serialization to Redis, and session TTL management.

---

### B. Agent Intelligence & Governance Layer (USM & NAD)

#### 4. `feature/bob-socratic-tutor`
- **Owner**: `usm`
- **Purpose**: Implementation of Bob (Socratic Tutor agent) with Pólya `<think>` deliberation logic and guiding question generation.

#### 5. `feature/alice-charlie-peers`
- **Owner**: `usm`
- **Purpose**: Implementation of Alice (Arithmetic Error Peer) and Charlie (Conceptual Error Peer) for realistic peer interactions.

#### 6. `feature/pedagogical-orchestrator`
- **Owner**: `usm`
- **Purpose**: LangGraph compiled state graph orchestrating candidate selection, utility scoring, and agent turn dispatching.

#### 7. `feature/assistance-hint-ladder`
- **Owner**: `usm`
- **Purpose**: 6-level assistance ladder transitions (Independent -> Gentle Nudge -> Guiding Question -> Worked Example -> Step-by-Step -> Direct Instruction).

#### 8. `feature/mastery-struggle-detection`
- **Owner**: `usm`
- **Purpose**: Struggle score calculation algorithm, concept attempt history, and mastery tracking.

#### 9. `subfeature/mastery-struggle/recovery-state-machine`
- **Owner**: `usm`
- **Purpose**: Recovery FSM managing transition states (`normal`, `scaffold`, `prerequisite_repair`, `micro_teaching`).

#### 10. `feature/leak-judge`
- **Owner**: `nad`
- **Purpose**: Domain-specific Leak Judge preventing agents from leaking complete math solutions or final step answers.

#### 11. `feature/help-judge-rewriter`
- **Owner**: `nad`
- **Purpose**: Helpfulness Judge evaluating Socratic guidance quality and Policy Rewriter regenerating non-compliant responses.

#### 12. `feature/adversarial-resistance`
- **Owner**: `nad`
- **Purpose**: Defense against prompt injection, rule overriding, and answer extraction attacks.

---

### C. Spatial UI & Observability / Evaluation Layer (MUW)

#### 13. `feature/prism-pipeline-instrumentation`
- **Owner**: `muw`
- **Purpose**: Block Convey PRISM SDK (`prismtrace-sdk>=0.4.3`) integration, ambient session management (`with prismtrace.session(session_id)`), non-blocking telemetry client (`prism_client.py`), and setup doctor handshake.
- **Key Files**: `backend/app/telemetry/prism_client.py`, `backend/app/config.py`, `backend/app/api/ws_router.py`, `docs/branches/feature-prism-pipeline-instrumentation.md`.

#### 14. `subfeature/prism/seven-pillar-scoring`
- **Owner**: `muw`
- **Purpose**: Quantitative 7-pillar evaluation engine (`seven_pillar_scorer.py`), SHA-256 signed Trust Pack artifact exporter (`trust_pack_exporter.py`), and evaluation API endpoint (`POST /api/v1/test/run-prism-suite`).
- **Key Files**: `backend/app/telemetry/seven_pillar_scorer.py`, `backend/app/telemetry/trust_pack_exporter.py`, `backend/app/api/eval_routes.py`.

#### 15. `subfeature/prism/adversarial-test-suite` *(Active HEAD)*
- **Owner**: `muw`
- **Purpose**: Automated adversarial resistance test battery (`test_adversarial_suite.py`) testing answer forcing, prompt injection, blackboard leakage, multi-turn extraction, and PRISM failure isolation.
- **Key Files**: `backend/tests/adversarial/test_adversarial_suite.py`, `docs/branches/feature-muw-implementation.md`.

---

## 3. Verification & Test Suite Summary

All 56 unit and adversarial tests pass cleanly across the telemetry, 7-pillar engine, Trust Pack exporter, and contract suites:

```bash
# Run full backend test suite across all branches
./.venv/bin/pytest -q backend
# Result: 56 passed in 7.20s
```
