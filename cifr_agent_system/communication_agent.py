import os
from google.cloud import language_v1
import base64
import google.genai as genai  # Correct import for Gemini
from cifr_agent_system.knowledge_agent import KnowledgeAgent
from .config import Config # Import the Config class

# Load environment variables from .env file (now handled in Config)

class CommunicationAgent:
    def __init__(self, project_id: str, knowledge_agent: KnowledgeAgent, location: str = Config.GCP_LOCATION):
        self.project_id = project_id
        self.location = location
        # Initialize the genai client with API key
        self.genai_client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.nlp_client = language_v1.LanguageServiceClient()
        self.knowledge_agent = knowledge_agent
        # Initialize other multimodal clients if needed, e.g., for vision

    def analyze_text(self, text: str):
        """Analyzes text for sentiment and entities."""
        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = self.nlp_client.analyze_sentiment(document=document).document_sentiment
        entities = self.nlp_client.analyze_entities(document=document).entities
        return {"sentiment": sentiment, "entities": entities}

    def analyze_multimodal_content(self, text_content: str, image_bytes: bytes = None):
        """Analyzes multimodal content using Gemini Pro Vision; falls back to heuristic/text when unavailable."""

        contents = []

        if text_content:
            contents.append({"parts": [{"text": text_content}]})

        if image_bytes:
            # For google.genai, encode image bytes to base64
            import base64
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            contents.append({
                "parts": [{
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": encoded_image
                    }
                }]
            })

        if not contents:
            raise ValueError("No content provided for multimodal analysis.")

        try:
            response = self.genai_client.models.generate_content(
                model=Config.GEMINI_PRO_VISION_MODEL_ID,
                contents=contents
            )

            if response.candidates:
                gemini_text_response = response.candidates[0].content.parts[0].text
                print("Gemini Response Text:", gemini_text_response)
                nlp_analysis_on_gemini_response = self.analyze_text(gemini_text_response)
                return {"gemini_response_text": gemini_text_response, "nlp_analysis": nlp_analysis_on_gemini_response}
            else:
                return {"error": "Gemini returned no candidates."}
        except Exception as e:
            # Fallback heuristic when Gemini is unavailable or quota-exhausted.
            print(f"Error calling Gemini: {e}")
            # Heuristic fallback for demo when Gemini is unavailable or quota-exhausted.
            print(f"Gemini API call failed: {e}. Providing heuristic analysis.")
            sentiment_score = 0.0
            lowered_text = text_content.lower()

            # Simple keyword-based sentiment for demo
            if any(keyword in lowered_text for keyword in ["frustrated", "angry", "delay", "issue", "slipping", "concerned", "problem"]):
                sentiment_score = -0.6
            elif any(keyword in lowered_text for keyword in ["great", "good", "happy", "success", "progress"]):
                sentiment_score = 0.7
            else:
                sentiment_score = 0.1 # Neutral to slightly positive default

            # Mock Entity objects for demo
            mock_entities = []
            if "delay" in lowered_text:
                mock_entities.append(type("Entity", (), {"name": "delay", "type_": language_v1.Entity.Type.EVENT, "salience": 0.8}))
            if "issue" in lowered_text:
                mock_entities.append(type("Entity", (), {"name": "issue", "type_": language_v1.Entity.Type.OTHER, "salience": 0.7}))
            
            # Mock the full NLP analysis structure
            mock_nlp_analysis = {
                "sentiment": type("Sentiment", (), {"score": sentiment_score, "magnitude": abs(sentiment_score)}),
                "entities": mock_entities
            }

            return {
                "error": f"Gemini API call failed: {e}. Heuristic analysis provided.",
                "gemini_response_text": f"Heuristic analysis: Text suggests a sentiment score of {sentiment_score:.2f}.",
                "nlp_analysis": mock_nlp_analysis,
            }

    def detect_friction(self, analysis_results: dict):
        """Detects potential friction points based on analysis results."""
        # Now, if Gemini provides an NLP analysis, use that for friction detection.
        sentiment_score = 0.0 # Default to neutral sentiment if not found
        if "nlp_analysis" in analysis_results and "sentiment" in analysis_results["nlp_analysis"]:
            sentiment_score = analysis_results["nlp_analysis"]["sentiment"].score
        elif "sentiment" in analysis_results and analysis_results["sentiment"]: # Fallback to direct NLP if no Gemini NLP
            sentiment_score = analysis_results["sentiment"].score

        if sentiment_score < -0.2:
            return {"friction_detected": True, "reason": "Negative sentiment detected", "severity": abs(sentiment_score)}
        return {"friction_detected": False}

    def process_collaboration_message(self, message: dict):
        """Processes an incoming collaboration message (e.g., chat, email)."""
        text_content = message.get("text_content", "")
        image_bytes = message.get("image_bytes")

        analysis_result = self.analyze_multimodal_content(text_content, image_bytes)
        
        analysis = analysis_result
        if "error" in analysis_result:
            print(f"Warning: Multimodal analysis failed: {analysis_result['error']}")
            # If multimodal analysis failed, ensure the 'analysis' dict still has a structure for downstream agents.
            # The heuristic in analyze_multimodal_content already provides this, so we just use it.
            analysis = analysis_result

        # The `detect_friction` method now needs to safely access `nlp_analysis` from the `analysis` dict.
        friction = self.detect_friction(analysis)

        message_id = message.get("message_id", f"message_{hash(frozenset(message.items()))}") # Generate a unique ID for the message
        self.knowledge_agent.store_context(f"communication_analysis_{message_id}", {
            "message": message,
            "analysis": analysis,
            "friction": friction,
            "timestamp": message.get("timestamp")
        })

        return {"analysis": analysis, "friction": friction}


if __name__ == "__main__":
    # Removed direct os.getenv for project_id as it's handled by Config now
    if not Config.GCP_PROJECT_ID:
        print("Please set the GCP_PROJECT_ID environment variable in your .env file.")
    else:
        # Create a dummy KnowledgeAgent instance for demonstration purposes
        dummy_knowledge_agent = KnowledgeAgent(project_id=Config.GCP_PROJECT_ID, location=Config.GCP_LOCATION)
        agent = CommunicationAgent(project_id=Config.GCP_PROJECT_ID, knowledge_agent=dummy_knowledge_agent, location=Config.GCP_LOCATION)

        # Example with text only
        sample_text_message = {
            "text_content": "I am really frustrated with the constant delays on this feature. We need to accelerate!",
            "timestamp": "2023-10-27T10:00:00Z",
            "sender": "Alice from Company A"
        }
        print("\n--- Analyzing text-only message ---")
        async def run_text_example():
            results = await agent.process_collaboration_message(sample_text_message)
            print(results)
        import asyncio
        asyncio.run(run_text_example())

        # Example with text and image (dummy image for demonstration)
        # In a real scenario, you would load image_bytes from a file, e.g.,
        # with open("path/to/your/image.jpg", "rb") as f:
        #     dummy_image_bytes = f.read()
        dummy_image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82"
        
        sample_multimodal_message = {
            "text_content": "This graph shows a significant drop in user engagement.",
            "image_bytes": dummy_image_bytes,
            "timestamp": "2023-10-27T11:00:00Z",
            "sender": "Bob from Company B"
        }
        print("\n--- Analyzing multimodal message ---")
        async def run_multimodal_example():
            results = await agent.process_collaboration_message(sample_multimodal_message)
            print(results)
        asyncio.run(run_multimodal_example())

        print("\nProject setup and multimodal analysis example complete.")
