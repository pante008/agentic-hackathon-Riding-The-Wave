import os
from typing import Dict, Any
import google.genai as genai
from .knowledge_agent import KnowledgeAgent
from .friction_detection_agent import FrictionDetectionAgent
from .config import Config

class InterventionAgent:
    def __init__(
        self,
        project_id: str,
        knowledge_agent: KnowledgeAgent,
        friction_detection_agent: FrictionDetectionAgent | None = None,
        location: str = Config.GCP_LOCATION,
    ):
        self.project_id = project_id
        self.location = location
        self.knowledge_agent = knowledge_agent
        self.friction_detection_agent = friction_detection_agent
        self.genai_client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    def suggest_intervention(self, communication_analysis_id: str) -> Dict[str, Any]:
        """Suggests interventions based on detected friction, calling specific intervention methods."""
        friction_results = self.friction_detection_agent.detect_communication_friction(communication_analysis_id)
        
        if "friction_detected" in friction_results and friction_results["friction_detected"]:
            # Retrieve the full communication data for context
            analysis_data = self.knowledge_agent.retrieve_context(communication_analysis_id)
            if not analysis_data:
                return {"intervention_suggested": False, "suggestion": "Friction detected but no analysis data found for intervention."}

            friction_reason = friction_results.get("reason", "").lower()

            # Example of dynamic intervention based on friction reason
            if "negative sentiment" in friction_reason or "frustrated" in friction_reason:
                suggestion_text = self.suggest_clarification(analysis_data)
                return {"intervention_suggested": True, "type": "clarification", "suggestion": suggestion_text, "details": friction_results}
            elif "delays" in friction_reason or "stalled" in friction_reason:
                suggestion_text = self.propose_action_item(analysis_data)
                return {"intervention_suggested": True, "type": "action_item", "suggestion": suggestion_text, "details": friction_results}
            elif "conflict" in friction_reason:
                suggestion_text = self.mediate_conflict(analysis_data)
                return {"intervention_suggested": True, "type": "mediation", "suggestion": suggestion_text, "details": friction_results}
            else:
                generic_suggestion = (
                    f"Friction detected due to: {friction_results.get('reason', 'Unknown reason')} "
                    f"(Severity: {friction_results.get('severity', 0.0):.2f}). "
                    "Consider a direct conversation or a general check-in."
                )
                return {"intervention_suggested": True, "type": "generic", "suggestion": generic_suggestion, "details": friction_results}
        else:
            # Handle cases where friction_detected is False or not present due to an error
            if "reason" in friction_results and "API error" in friction_results["reason"]:
                return {
                    "intervention_suggested": False,
                    "suggestion": f"Friction detection failed: {friction_results['reason']}",
                }
            else:
                return {"intervention_suggested": False, "suggestion": "No significant friction detected, no intervention needed."}

    def suggest_clarification(self, analysis_data: Dict[str, Any]) -> str:
        """Suggests a clarification message to address detected friction."""
        # ... (existing suggest_clarification logic remains)
        friction_details = analysis_data.get("friction", {})
        message_content = analysis_data.get("message", {}).get("text_content", "")
        sender = analysis_data.get("message", {}).get("sender", "")
        reason = friction_details.get("reason", "a potential issue")

        prompt = f"A potential friction point has been detected: '{reason}'. The original message was from {sender} and stated: \"\"{message_content}\"\". Please draft a concise and helpful message that could clarify this situation or suggest a next step to reduce friction. Focus on collaboration and understanding."

        try:
            response = self.genai_client.models.generate_content(
                model=Config.GEMINI_PRO_MODEL_ID,
                contents=[{"parts": [{"text": prompt}]}]
            )
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                return "Could not generate a clarification message."
        except Exception as e:
            print(f"Error calling Gemini for clarification suggestion: {e}")
            return f"Error generating clarification: {e}"

    def propose_action_item(self, analysis_data: Dict[str, Any]) -> str:
        """Proposes a specific action item to unblock a stalled decision."""
        # ... (existing propose_action_item logic remains)
        friction_details = analysis_data.get("friction", {})
        message_content = analysis_data.get("message", {}).get("text_content", "")
        issue_details = friction_details.get("reason", "") # Using friction reason as issue details for now

        prompt = f"A decision or action item is stalled. Details: {issue_details}. Based on this, please propose a clear, next actionable step that can unblock the situation. State who should be responsible (if inferable) and a suggested immediate action."

        try:
            response = self.genai_client.models.generate_content(
                model=Config.GEMINI_PRO_MODEL_ID,
                contents=[{"parts": [{"text": prompt}]}]
            )
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                return "Could not propose an action item."
        except Exception as e:
            print(f"Error calling Gemini for action item proposal: {e}")
            return f"Error proposing action item: {e}"

    def mediate_conflict(self, analysis_data: Dict[str, Any]) -> str:
        """Suggests mediation strategies for identified conflicts (placeholder)."""
        friction_details = analysis_data.get("friction", {})
        reason = friction_details.get("reason", "").lower()
        print(f"InterventionAgent: Mediating conflict: {reason}")
        return "Mediation strategy placeholder: Suggesting a joint discussion session to resolve differences."

if __name__ == "__main__":
    # Removed direct os.getenv for project_id as it's handled by Config now
    if not Config.GCP_PROJECT_ID:
        print("Please set the GCP_PROJECT_ID environment variable in your .env file.")
    else:
        knowledge_agent = KnowledgeAgent(project_id=Config.GCP_PROJECT_ID, location=Config.GCP_LOCATION)
        intervention_agent = InterventionAgent(project_id=Config.GCP_PROJECT_ID, knowledge_agent=knowledge_agent, location=Config.GCP_LOCATION)

        # Simulate storing some communication analysis
        sample_analysis_id = "comm_analysis_789"
        knowledge_agent.store_context(sample_analysis_id, {
            "message": {"text_content": "This project is falling behind, and I'm very concerned."},
            "analysis": {"sentiment": {"score": -0.6}},
            "friction": {"friction_detected": True, "reason": "Concern about project delays", "severity": 0.6},
            "timestamp": "2023-10-27T12:00:00Z"
        })

        # Suggest an intervention
        intervention = intervention_agent.suggest_clarification({"message": {"text_content": "This project is falling behind, and I'm very concerned."}, "reason": "Concern about project delays", "severity": 0.6})
        print("\n--- Intervention Suggestion ---")
        print(intervention)

        sample_analysis_id_2 = "comm_analysis_101"
        knowledge_agent.store_context(sample_analysis_id_2, {
            "message": {"text_content": "Great work on the latest sprint!"},
            "analysis": {"sentiment": {"score": 0.9}},
            "friction": {"friction_detected": False},
            "timestamp": "2023-10-27T13:00:00Z"
        })

        intervention_2 = intervention_agent.propose_action_item({"issues": ["Decision on sprint scope is pending", "No clear next step for team member A"]})
        print("\n--- Intervention Suggestion (No Friction) ---")
        print(intervention_2)
