from datetime import datetime
from typing import Any, Dict, List, Optional


class MemoryStore:
    """Lightweight in-memory log for executions and agent traces."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def log(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "event": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self.events.append(entry)
        return entry

    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if event_type is None:
            return list(self.events)
        return [e for e in self.events if e["event"] == event_type]

    def latest(self, n: int = 20) -> List[Dict[str, Any]]:
        return self.events[-n:]


