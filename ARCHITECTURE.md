# CIFR Agent System – Architecture

Aligned with the official Agentic AI Hackathon template ([odsc2015/agentic-hackathon-template](https://github.com/odsc2015/agentic-hackathon-template)).

## High-Level Overview
- Goal: Reduce intercompany friction via multi-agent collaboration.
- Gemini usage: `google.genai` for multimodal analysis, planning, and interventions.
- Delivery targets: CLI + Flask demo; cloud-ready with GCP services.

## Component Diagram (ASCII)
```
User Request (UI/CLI)
    │
    ▼
Planner (Gemini plan)
    │ plan
    ▼
Executor ──────────────────────────────────────────────┐
    │ dispatch                                          │
    ▼                                                   │
CommunicationAgent ──► KnowledgeAgent (context store)   │
           │                │                           │
           ▼                │                           │
  FrictionDetectionAgent ◄──┘                           │
           │                                            │
           ▼                                            │
    InterventionAgent → Response / Guidance to user     │
```

## Modules
- `src/planner.py`: Uses Gemini text to propose 3–6 JSON steps; heuristic fallback.
- `src/executor.py`: Iterates plan, calls agents, records trace.
- `src/memory.py`: Lightweight in-memory event log for demo traces.
- `cifr_agent_system/communication_agent.py`: Multimodal analysis (Gemini Vision/Text + Language API fallback).
- `cifr_agent_system/friction_detection_agent.py`: Misalignment detection (Gemini + heuristic keywords).
- `cifr_agent_system/intervention_agent.py`: Generates clarifications/action-items/mediation suggestions.
- `cifr_agent_system/knowledge_agent.py`: In-memory knowledge base (store/retrieve/search).
- `cifr_agent_system/config.py`: Env loading, optional insecure SSL for sandboxes, model IDs.

## Data Flow
1) User goal → Planner → structured steps.
2) Executor loops steps:
   - `analyze_messages`: CommunicationAgent performs multimodal analysis; stores context.
   - `detect_friction`: FrictionDetectionAgent reasons over stored context.
   - `generate_interventions`: InterventionAgent drafts guidance based on friction.
3) KnowledgeAgent stores analyses + interventions.
4) Executor returns results + trace to UI/CLI.

## Environment & Secrets
- `.env` (gitignored): `GCP_PROJECT_ID`, `GCP_LOCATION`, `GOOGLE_API_KEY` (or per-agent keys), `GEMINI_PRO_MODEL_ID`, `GEMINI_PRO_VISION_MODEL_ID`.
- `key.json` should not be committed; rotate/remove if ever added.
- `ALLOW_INSECURE_SSL=1` only for sandbox environments.

## Observability (current)
- Structured logging via `logging`; memory trace for demo.
- Flask API prints warnings for quota/heuristic fallbacks.

## Extension Ideas
- Persist memory to Firestore/Spanner and add retrieval to planner prompts.
- Add tool router for calendars/search and external actions.
- Integrate OpenTelemetry tracing; promote heuristics to typed fallbacks with scores.

