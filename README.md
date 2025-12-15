# CIFR Agent System (Agentic AI Hackathon)

This repo aligns with the [Agentic AI App Hackathon template](https://github.com/odsc2015/agentic-hackathon-template) and implements a multi-agent workflow for communication analysis, friction detection, and intervention suggestions using Google Gemini.

## Contents
- `src/`: hackathon-required planner/executor/memory modules.
- `cifr_agent_system/`: domain agents (communication, friction detection, intervention, knowledge, utils, config).
- `frontend/`: lightweight Flask UI for demo.
- Docs: `ARCHITECTURE.md`, `EXPLANATION.md`, `DEMO.md`, `API_KEY_SETUP.md`.

## Prerequisites
- Python 3.10+ recommended (works on 3.9 with shims, but prefer 3.10+).
- Google Gemini API key from Google AI Studio.
- GCP Project ID if using Cloud Language fallback.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r cifr_agent_system/requirements.txt
```

Create a `.env` (not committed) with:
```
GCP_PROJECT_ID=<project>
GCP_LOCATION=us-central1
GOOGLE_API_KEY=<gemini_api_key>
# Optional per-agent overrides
GOOGLE_API_KEY_CA=<communication_key>
GOOGLE_API_KEY_FA=<friction_key>
GOOGLE_API_KEY_IA=<intervention_key>
GEMINI_PRO_MODEL_ID=gemini-2.0-flash
GEMINI_PRO_VISION_MODEL_ID=gemini-2.5-flash
```

## Running
- CLI demo: `python -m cifr_agent_system.main`
- Flask UI: `python app.py` then open `http://localhost:5000`
- Planner/Executor programmatic use:
```python
from src.executor import Executor
from src.memory import MemoryStore
# instantiate agents from cifr_agent_system.*
```

## Hackathon Checklist (per template)
- Fork named after team/participant.
- Agent built under `src/` (planner/executor/memory present).
- Gemini API integrated (`google.genai` in planner + agents).
- Docs filled: `README.md`, `ARCHITECTURE.md`, `EXPLANATION.md`, `DEMO.md` (video link pending).
- Video demo to be recorded and linked in `DEMO.md`.

## Security & Secrets
- Do **not** commit `.env` or `key.json`. They are gitignored. Rotate any previously committed keys.
- Set `ALLOW_INSECURE_SSL=1` only in constrained sandboxes; keep unset for real deployments.

## Troubleshooting
- If Flask complains about `.env` permissions, set `FLASK_SKIP_DOTENV=1` (already defaulted in `app.py`).
- If Gemini quota is hit, agents fall back to heuristic logic and log warnings.

## License
Apache-2.0 (template baseline).

