# CIFR Agent System – Architecture

This document aligns the project with the official Agentic AI Hackathon template ([odsc2015/agentic-hackathon-template](https://github.com/odsc2015/agentic-hackathon-template)).

## High-Level Overview
- Goal: Reduce intercompany friction through multi-agent collaboration.
- Required Gemini usage: google.genai for multimodal analysis, planning, and interventions.
- Deployment target: local demo; cloud-ready via GCP.

## Component Diagram (ASCII)
```
User Request
    │
    ▼
 Planner (Gemini plan)
    │ plan
    ▼
 Executor ───────────────┐
    │ executes            │
    ▼                     │
 CommunicationAgent ──► KnowledgeAgent (shared memory)
            │                │
            ▼                │
   FrictionDetectionAgent ◄──┘
            │
            ▼
     InterventionAgent → User-facing guidance
```

## Modules
- `src/planner.py`: Breaks user goals into sub-tasks via Gemini text model.
- `src/executor.py`: Coordinates planner output with existing agents and tracks trace/logs.
- `src/memory.py`: Lightweight in-memory log; complements `KnowledgeAgent`.
- `cifr_agent_system/*`: Original specialized agents (communication, friction, intervention, knowledge, utils).

## Data Flow
1) User goal enters Planner → structured steps.
2) Executor routes steps:
   - Analyze messages (CommunicationAgent + Gemini Vision/Text).
   - Detect misalignment (FrictionDetectionAgent + Gemini).
   - Generate interventions (InterventionAgent + Gemini).
3) KnowledgeAgent stores all analyses and interventions.
4) Executor returns combined trace/results for demo or API.

## Environment & Secrets
- `.env` (not committed): `GCP_PROJECT_ID`, `GCP_LOCATION`, `GOOGLE_API_KEY`, `GEMINI_PRO_MODEL_ID`, `GEMINI_PRO_VISION_MODEL_ID`.
- `key.json` must not be committed; rotate/remove from history if already tracked.

## Observability (current)
- CLI prints and lightweight metrics in `main.py`.
- Web dashboard (Flask) optional for live metrics.

## Extension Ideas
- Persist memory to a database (Firestore/Spanner).
- Add tool router for external APIs (search, calendars).
- Add tracing (OpenTelemetry) and structured logging for demo.


