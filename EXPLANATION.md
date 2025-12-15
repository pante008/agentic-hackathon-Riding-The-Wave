# CIFR Agent System – Explanation

This document follows the Agentic AI Hackathon template requirements.

## Planning Style
- Planner uses Gemini text model (`google.genai`) to turn user goals into 3–6 sub-tasks.
- Output format: JSON list with `id`, `action`, `input`, `notes`, `expected_output`.
- Fallback heuristics ensure planning works even if Gemini is unavailable.

## Execution Flow
1) Planner creates steps.
2) Executor iterates steps and routes to agents:
   - `analyze_messages` → CommunicationAgent (Gemini Vision/Text + Language API).
   - `detect_friction` → FrictionDetectionAgent (Gemini reasoning).
   - `generate_interventions` → InterventionAgent (Gemini suggestions).
3) Results and reasoning traces are stored in KnowledgeAgent and Memory store.

## Memory Usage
- `KnowledgeAgent` maintains contextual store for analyses and recommendations.
- `src/memory.py` provides a lightweight append-only log for executions.
- Future: persist to datastore and add retrieval-augmented prompts.

## Tool Integration
- Gemini API via `google.genai` for:
  - Multimodal analysis (CommunicationAgent).
  - Friction reasoning (FrictionDetectionAgent).
  - Intervention drafting (InterventionAgent).
  - Planning (Planner).
- GCP language services for sentiment/entities as a fallback/augmenter.

## Limitations
- Requires valid `GOOGLE_API_KEY`; Config raises if missing.
- Memory is in-process only; no persistence yet.
- Planning/exec parsing assumes well-formed Gemini JSON; guarded with fallbacks.
- Demo uses synthetic messages; real integrations (Slack/Gmail/Drive) are stubs.

## Known Risks
- `key.json` is present locally; remove from git history and rely on `.env`.
- Network/API failures degrade to heuristic flows; add retries/backoff for prod.


