# CIFR Agent System – Demo

Provide a public 3–5 minute video link here (YouTube unlisted, Drive public, Loom, etc.). Submissions without a valid link will not be reviewed.

## Video Link
- TODO: Paste final link here after recording.

## Timestamped Highlights
- 00:00–00:30 Intro & setup
- 00:30–01:30 User input → Planning (Planner + Executor)
- 01:30–02:30 Tool calls & memory (CommunicationAgent, KnowledgeAgent, FrictionDetectionAgent)
- 02:30–03:30 Final output & edge cases (InterventionAgent + fallback flows)

## How to Reproduce
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -r cifr_agent_system/requirements.txt`
3) Create `.env` with `GCP_PROJECT_ID`, `GOOGLE_API_KEY`, optional `GEMINI_PRO_MODEL_ID`, `GEMINI_PRO_VISION_MODEL_ID`.
4) Run `python -m cifr_agent_system.main` for the CLI demo.
5) (Optional) Run web dashboard via option 2 in the menu.


