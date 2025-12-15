import os
from typing import Dict, Any
import google.genai as genai
from .knowledge_agent import KnowledgeAgent
from .config import Config

class FrictionDetectionAgent:
    def __init__(self, project_id: str, knowledge_agent: KnowledgeAgent, location: str = Config.GCP_LOCATION):
        self.project_id = project_id
        self.location = location
        self.knowledge_agent = knowledge_agent
        # Initialize the genai client with API key
        self.genai_client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    def detect_communication_friction(self, analysis_id: str) -> Dict[str, Any]:
        """
        Compatibility helper for web API:
        - Retrieves stored communication analysis from KnowledgeAgent by ID.
        - Delegates to detect_misalignment for reasoning.
        """
        context = self.knowledge_agent.retrieve_context(analysis_id) or {}
        return self.detect_misalignment(context)

    def detect_misalignment(self, communication_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detects potential misalignments or conflicts based on communication analysis and knowledge base."""
        # Placeholder logic: In a real scenario, this would involve comparing statements,
        # action items, and goals stored in the knowledge base, potentially using Gemini
        # for advanced reasoning over the aggregated context.

        text_content = communication_analysis.get("message", {}).get("text_content", "")
        sender = communication_analysis.get("message", {}).get("sender", "Unknown")

        prompt = f"Given the following communication from {sender}: \"\"{text_content}\"\". Analyze this statement for any potential misalignments, conflicting goals, or hidden frictions with general project objectives or other known team statements. Explain your reasoning. If no friction, state 'No friction detected'."

        try:
            response = self.genai_client.models.generate_content(
                model=Config.GEMINI_PRO_MODEL_ID,
                contents=[{"parts": [{"text": prompt}]}]
            )
            if response.candidates and response.candidates[0].content.parts:
                gemini_response = response.candidates[0].content.parts[0].text
                print(f"FrictionDetectionAgent (Gemini): {gemini_response}")

                # Simple heuristic to parse friction detection from Gemini's response
                if "no friction detected" in gemini_response.lower():
                    return {"friction_detected": False, "reason": gemini_response}
                else:
                    return {"friction_detected": True, "reason": gemini_response}
            else:
                return {"misalignment_detected": False, "reason": "Gemini returned no valid content.", "severity": 0.0}
        except Exception as e:
            # Fallback heuristic for demo when quota is exhausted or Gemini fails.
            print(f"Error calling Gemini for friction detection: {e}")
            lowered = text_content.lower()
            friction_keywords = ["frustrated", "delay", "issue", "slipping", "angry", "upset"]
            hit = any(k in lowered for k in friction_keywords)
            if hit:
                return {
                    "friction_detected": True,
                    "reason": "Heuristic friction detected (Gemini unavailable)",
                    "severity": 0.6,
                }
            return {
                "friction_detected": False,
                "reason": f"Gemini unavailable; heuristic shows no friction ({e})",
                "severity": 0.0,
            }

    def identify_stalled_decisions(self) -> Dict[str, Any]:
        """Identifies decisions that are stalled or overdue (placeholder)."""
        # This would typically query the knowledge base for tracked decisions and their statuses.
        print("FrictionDetectionAgent: Identifying stalled decisions...")
        # Example: Retrieve all communication analyses and look for keywords indicating decisions or actions
        all_communications = self.knowledge_agent.search_knowledge("communication_analysis")
        stalled_issues = []
        for key, value in all_communications.items():
            if "friction" in value and value["friction"].get("friction_detected"):
                if "delay" in value["message"].get("text_content", "").lower(): # Simple keyword check for now
                    stalled_issues.append(value["message"])
        
        if stalled_issues:
            return {"stalled_decisions_detected": True, "issues": stalled_issues}
        return {"stalled_decisions_detected": False}

if __name__ == "__main__":
    # Removed direct os.getenv for project_id as it's handled by Config now
    if not Config.GCP_PROJECT_ID:
        print("Please set the GCP_PROJECT_ID environment variable in your .env file.")
    else:
        knowledge_agent = KnowledgeAgent(project_id=Config.GCP_PROJECT_ID, location=Config.GCP_LOCATION)
        friction_agent = FrictionDetectionAgent(project_id=Config.GCP_PROJECT_ID, knowledge_agent=knowledge_agent, location=Config.GCP_LOCATION)

        # Simulate storing some communication analysis
        sample_analysis_id = "comm_analysis_123"
        knowledge_agent.store_context(sample_analysis_id, {
            "message": {"text_content": "This is a frustrated message."},
            "analysis": {"sentiment": {"score": -0.8}},
            "friction": {"friction_detected": True, "reason": "Negative sentiment", "severity": 0.8},
            "timestamp": "2023-10-27T10:00:00Z"
        })

        # Detect friction using the stored analysis
        friction_agent.detect_communication_friction(sample_analysis_id)

        sample_analysis_id_2 = "comm_analysis_456"
        knowledge_agent.store_context(sample_analysis_id_2, {
            "message": {"text_content": "This is a positive message."},
            "analysis": {"sentiment": {"score": 0.7}},
            "friction": {"friction_detected": False},
            "timestamp": "2023-10-27T11:00:00Z"
        })

        friction_agent.detect_communication_friction(sample_analysis_id_2)
