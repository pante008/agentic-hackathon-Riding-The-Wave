import json
import os
from typing import Any, Dict, List, Optional

try:
    import google.genai as genai
except ImportError:
    genai = None


def _make_client() -> Optional[Any]:
    """Create a Gemini client if api key and library are available."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or genai is None:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


def _parse_candidate(raw_text: str) -> List[Dict[str, Any]]:
    """Parse Gemini JSON output into a list of steps."""
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict) and "steps" in data and isinstance(data["steps"], list):
            return data["steps"]
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def plan(goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Produce a task plan for the goal.
    Returns {source, steps, raw_response, error}.
    """
    context = context or {}
    steps: List[Dict[str, Any]] = []
    raw_response = None
    error = None

    client = _make_client()
    if goal and client:
        prompt = (
            "You are a planner. Create 3-6 JSON steps to satisfy the goal. "
            "Each step must have: id, action, input, notes, expected_output. "
            f"Goal: {goal}\nContext: {json.dumps(context)[:1500]}"
        )
        try:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_PRO_MODEL_ID", "gemini-2.0-flash"),
                contents=[{"parts": [{"text": prompt}]}],
            )
            if response.candidates and response.candidates[0].content.parts:
                raw_response = response.candidates[0].content.parts[0].text
                steps = _parse_candidate(raw_response)
        except Exception as exc:  # pragma: no cover - network/Gemini issues
            error = str(exc)

    if not steps:
        # Fallback heuristic plan
        steps = [
            {"id": "1", "action": "analyze_messages", "input": "ingest and analyze messages", "notes": "use CommunicationAgent", "expected_output": "message analyses"},
            {"id": "2", "action": "detect_friction", "input": "use analyses", "notes": "call FrictionDetectionAgent", "expected_output": "friction report"},
            {"id": "3", "action": "generate_interventions", "input": "friction report", "notes": "call InterventionAgent", "expected_output": "recommended actions"},
        ]
        source = "heuristic"
    else:
        source = "gemini"

    return {"source": source, "steps": steps, "raw_response": raw_response, "error": error}


