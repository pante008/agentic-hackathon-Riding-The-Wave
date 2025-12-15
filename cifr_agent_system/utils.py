# cifr_agent_system/utils.py

import uuid

def generate_unique_id(prefix: str = "id") -> str:
    """Generates a simple unique ID."""
    return f"{prefix}_{uuid.uuid4()}"

