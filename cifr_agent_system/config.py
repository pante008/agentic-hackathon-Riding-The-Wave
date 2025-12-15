import os
import ssl
from dotenv import load_dotenv

# Allow opting into insecure SSL only when explicitly requested (for sandboxes).
ALLOW_INSECURE_SSL = os.getenv("ALLOW_INSECURE_SSL", "0") == "1"

if ALLOW_INSECURE_SSL:
    def _no_verify_context(*args, **kwargs):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    ssl._create_default_https_context = _no_verify_context
    ssl.create_default_context = _no_verify_context
    ssl._create_unverified_context = _no_verify_context

# Ensure SSL_CERT_FILE points to a readable cert bundle (to avoid permission errors
# when the default system cert store is blocked in sandboxed environments).
try:
    import certifi
    cert_path = certifi.where()
    os.environ["SSL_CERT_FILE"] = cert_path
    os.environ["REQUESTS_CA_BUNDLE"] = cert_path
    os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = cert_path
except Exception:
    pass

# Load environment variables from .env file; if unreadable (permissions/sandbox), fall back to existing env.
try:
    load_dotenv()
except PermissionError:
    print("Warning: cifr_agent_system/.env not readable; relying on existing environment variables.")

class Config:
    # GCP Project Settings
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1") # Default to us-central1
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Legacy single key / default
    GOOGLE_API_KEY_CA = os.getenv("GOOGLE_API_KEY_CA")  # Communication Agent
    GOOGLE_API_KEY_FA = os.getenv("GOOGLE_API_KEY_FA")  # Friction Detection Agent
    GOOGLE_API_KEY_IA = os.getenv("GOOGLE_API_KEY_IA")  # Intervention Agent

    # Vertex AI / Gemini Settings
    VERTEX_AI_ENDPOINT = f"{GCP_LOCATION}-aiplatform.googleapis.com"
    GEMINI_PRO_VISION_MODEL_ID = os.getenv("GEMINI_PRO_VISION_MODEL_ID", "gemini-2.5-flash")
    GEMINI_PRO_MODEL_ID = os.getenv("GEMINI_PRO_MODEL_ID", "gemini-2.0-flash")

    # HTTP options for google.genai; disable SSL verification in constrained environments.
    GENAI_HTTP_OPTIONS = {"verify": False}

    # OpenAI-Compatible Fallback Service (Secondary - for demo/backup only)
    # NOTE: Hackathon judges won't have access to this service
    # This is only used as fallback when free tier Google Gemini API hits quota limits
    OPENAI_FALLBACK_BASE_URL = os.getenv("OPENAI_FALLBACK_BASE_URL")  # e.g., https://caas-gocode-prod.caas-prod.prod.onkatana.net/v1
    OPENAI_FALLBACK_API_KEY = os.getenv("OPENAI_FALLBACK_API_KEY")  # OpenAI-compatible API key
    OPENAI_FALLBACK_MODEL = os.getenv("OPENAI_FALLBACK_MODEL", "gemini-2.0-flash-001")  # Model name on fallback service
    ENABLE_OPENAI_FALLBACK = os.getenv("ENABLE_OPENAI_FALLBACK", "0") == "1"  # Set to "1" to enable fallback

    # Ensure required environment variables are set
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")
    if not (GOOGLE_API_KEY or GOOGLE_API_KEY_CA or GOOGLE_API_KEY_FA or GOOGLE_API_KEY_IA):
        raise ValueError("No Gemini API key found. Set GOOGLE_API_KEY or per-agent keys GOOGLE_API_KEY_CA/FA/IA. Get your API key from https://aistudio.google.com/app/apikey")

    # Add other configuration variables as needed (e.g., database settings)
