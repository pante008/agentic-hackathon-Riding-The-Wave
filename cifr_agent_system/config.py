import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # GCP Project Settings
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1") # Default to us-central1
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # For Google AI API (genai)

    # Vertex AI / Gemini Settings
    VERTEX_AI_ENDPOINT = f"{GCP_LOCATION}-aiplatform.googleapis.com"
    GEMINI_PRO_VISION_MODEL_ID = os.getenv("GEMINI_PRO_VISION_MODEL_ID", "gemini-2.5-flash")
    GEMINI_PRO_MODEL_ID = os.getenv("GEMINI_PRO_MODEL_ID", "gemini-2.0-flash")

    # Ensure required environment variables are set
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set. Get your API key from https://aistudio.google.com/app/apikey")

    # Add other configuration variables as needed (e.g., database settings)
