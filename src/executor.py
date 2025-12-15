import logging
from typing import Any, Dict, List, Optional
from src.memory import MemoryStore
from src import planner

logger = logging.getLogger(__name__)


class Executor:
    """
    Coordinates planning and tool/agent calls.
    Expects injected agents to keep dependencies explicit for the hackathon template.
    """

    def __init__(
        self,
        communication_agent: Any,
        friction_detection_agent: Any,
        intervention_agent: Any,
        knowledge_agent: Any,
        memory_store: Optional[MemoryStore] = None,
    ):
        self.communication_agent = communication_agent
        self.friction_detection_agent = friction_detection_agent
        self.intervention_agent = intervention_agent
        self.knowledge_agent = knowledge_agent
        self.memory = memory_store or MemoryStore()

    def execute_plan(
        self,
        goal: str,
        messages: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plan_result = planner.plan(goal, context)
        self.memory.log("plan_created", {"goal": goal, "plan": plan_result})

        results: List[Dict[str, Any]] = []

        for step in plan_result["steps"]:
            action = step.get("action")

            if action == "analyze_messages":
                for message in messages:
                    analysis = self.communication_agent.process_collaboration_message(message)
                    self.memory.log("analysis", {"message": message, "analysis": analysis})
                    results.append({"step": step["id"], "type": "analysis", "result": analysis})

            elif action == "detect_friction":
                for message in messages:
                    context_key = f"communication_analysis_{message.get('message_id', 'demo_msg')}"
                    stored = self.knowledge_agent.retrieve_context(context_key) or {"message": message}
                    friction = self.friction_detection_agent.detect_misalignment(stored)
                    self.memory.log("friction_detection", {"message": message, "friction": friction})
                    results.append({"step": step["id"], "type": "friction", "result": friction})

            elif action == "generate_interventions":
                for message in messages:
                    context_key = f"communication_analysis_{message.get('message_id', 'demo_msg')}"
                    stored = self.knowledge_agent.retrieve_context(context_key) or {"message": message}
                    friction = stored.get("friction", {})
                    intervention = self.intervention_agent.suggest_clarification(
                        {"message": stored.get("message", {}), "reason": friction.get("reason", "")}
                    )
                    self.memory.log("intervention", {"message": message, "intervention": intervention})
                    results.append({"step": step["id"], "type": "intervention", "result": intervention})

            else:
                # Unknown action; log and continue
                logger.warning("Skipped unknown action: %s", action)
                self.memory.log("skipped_step", {"step": step})
                results.append({"step": step.get("id"), "type": "skipped", "reason": "unknown action"})

        return {"plan": plan_result, "results": results, "trace": self.memory.latest()}


