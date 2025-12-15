import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import base64
import json

# Flask CLI tries to auto-load .env and can crash if the file isn't readable.
# Prevent that and rely on our explicit load_dotenv below.
os.environ.setdefault("FLASK_SKIP_DOTENV", "1")

# Ensure environment variables are loaded for Config to access them.
# If the .env file is not readable (e.g., permissions or sandbox filters),
# fall back to existing environment variables.
try:
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except PermissionError:
    print("Warning: .env not readable; relying on existing environment variables.")

# Import agents and Config from your cifr_agent_system package
from cifr_agent_system.config import Config
from cifr_agent_system.communication_agent import CommunicationAgent
from cifr_agent_system.knowledge_agent import KnowledgeAgent
from cifr_agent_system.friction_detection_agent import FrictionDetectionAgent
from cifr_agent_system.intervention_agent import InterventionAgent
from cifr_agent_system.utils import generate_unique_id


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def serialize_google_cloud_object(obj):
    """Recursively converts Google Cloud client library objects to JSON serializable types."""
    # Handle dicts first (before checking __dict__)
    if isinstance(obj, dict):
        return {k: serialize_google_cloud_object(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        # Recursively process lists/tuples
        return [serialize_google_cloud_object(elem) for elem in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        # Handle Google Cloud protobuf objects
        if hasattr(obj, '_pb'):
            return serialize_google_cloud_object(obj._pb)
        # Recursively process dictionary-like objects
        return {k: serialize_google_cloud_object(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    # Handle specific Google Cloud client objects like Sentiment.score, Sentiment.magnitude, and Entities
    elif hasattr(obj, 'score') and hasattr(obj, 'magnitude'):
        return {"score": obj.score, "magnitude": obj.magnitude}
    elif hasattr(obj, 'entities') and isinstance(obj.entities, (list, tuple)):
        return [serialize_google_cloud_object(entity) for entity in obj.entities]
    elif hasattr(obj, 'name') and hasattr(obj, 'type_') and hasattr(obj, 'salience'):
        return {"name": obj.name, "type": str(obj.type_), "salience": obj.salience}
    elif hasattr(obj, 'name') and hasattr(obj, 'confidence'):
        return {"name": obj.name, "confidence": obj.confidence}
    # Handle generic protobuf messages by converting to a dictionary
    elif hasattr(obj, 'DESCRIPTOR') and hasattr(obj, 'ListFields'):
        return {field.name: serialize_google_cloud_object(getattr(obj, field.name)) for field, _ in obj.ListFields()}
    # Base cases for primitive types
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    # For any other object type, try to stringify or represent as dict
    else:
        try:
            # Try to convert to dict if it has to_dict or similar method
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            # Or just convert to string representation for unknown complex objects
            return str(obj)
        except Exception:
            return f"<Unserializable Object: {type(obj).__name__}>"

app = Flask(__name__, 
            static_folder='./frontend/static',
            template_folder='./frontend/templates')

# Initialize agents globally or per-request if state management is complex
# For simplicity, we'll initialize them globally here.
logger.info("🤖 CIFR Agent System - Initializing Agents")
logger.info("📋 Project ID: %s", Config.GCP_PROJECT_ID)
logger.info("📍 Location: %s", Config.GCP_LOCATION)
logger.info(
    "🔑 API Key Configuration: default=%s, CA=%s, FA=%s, IA=%s",
    "set" if Config.GOOGLE_API_KEY else "missing",
    "dedicated" if Config.GOOGLE_API_KEY_CA else "default",
    "dedicated" if Config.GOOGLE_API_KEY_FA else "default",
    "dedicated" if Config.GOOGLE_API_KEY_IA else "default",
)

knowledge_agent = KnowledgeAgent(project_id=Config.GCP_PROJECT_ID, location=Config.GCP_LOCATION)
communication_agent = CommunicationAgent(project_id=Config.GCP_PROJECT_ID, knowledge_agent=knowledge_agent, location=Config.GCP_LOCATION)
friction_detection_agent = FrictionDetectionAgent(project_id=Config.GCP_PROJECT_ID, knowledge_agent=knowledge_agent, location=Config.GCP_LOCATION)
intervention_agent = InterventionAgent(project_id=Config.GCP_PROJECT_ID, knowledge_agent=knowledge_agent, friction_detection_agent=friction_detection_agent, location=Config.GCP_LOCATION)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process_message', methods=['POST'])
def process_message_api():
    data = request.form
    text_content = data.get('text_content', '')
    image_file = request.files.get('image_file')

    image_bytes = None
    if image_file:
        image_bytes = image_file.read()

    message_id = generate_unique_id("web_message")
    timestamp = datetime.now().isoformat()

    sample_message = {
        "message_id": message_id,
        "text_content": text_content,
        "image_bytes": image_bytes,
        "timestamp": timestamp,
        "sender": "Web User"
    }

    logger.info("[API] Processing message ID: %s", message_id)

    results = {
        "original_message": sample_message,
        "communication_analysis": None,
        "knowledge_update_status": None,
        "friction_detection": None,
        "intervention_suggestion": None,
        "error": None,
        "warnings": []
    }

    try:
        # 1. Communication Agent processing
        comm_agent_results = communication_agent.process_collaboration_message(sample_message)
        logger.debug("Communication agent results type: %s", type(comm_agent_results))
        # Ensure proper JSON serialization - always return a dict, never a string
        comm_serialized = serialize_google_cloud_object(comm_agent_results)
        logger.debug("After serialization, type: %s, is dict: %s", type(comm_serialized), isinstance(comm_serialized, dict))
        # Ensure it's a dict, not a string
        if isinstance(comm_serialized, str):
            logger.warning("Communication analysis was serialized as string! Attempting to parse...")
            try:
                comm_serialized = json.loads(comm_serialized)
            except:
                logger.warning("JSON parse failed, trying Python literal eval")
                import ast
                try:
                    comm_serialized = ast.literal_eval(comm_serialized)
                except Exception as e:
                    logger.error("Failed to parse communication analysis: %s", e)
                    comm_serialized = {"error": "Failed to parse communication analysis", "raw": comm_serialized[:200]}
        if not isinstance(comm_serialized, dict):
            logger.error("Communication analysis is not a dict after processing! Type: %s", type(comm_serialized))
            comm_serialized = {"error": "Invalid response format", "type": str(type(comm_serialized))}
        results["communication_analysis"] = comm_serialized
        results["knowledge_update_status"] = "Context stored under 'communication_analysis_{}'".format(message_id)
        
        # Check for quota errors and API source in communication analysis
        comm_str = json.dumps(comm_serialized) if isinstance(comm_serialized, dict) else str(comm_agent_results)
        if "429" in comm_str or "RESOURCE_EXHAUSTED" in comm_str or "quota" in comm_str.lower():
            results["warnings"].append("Communication Agent: Gemini API quota exceeded. Using fallback service.")
        # Check if using fallback service
        analysis = comm_serialized.get("analysis", {}) if isinstance(comm_serialized, dict) else {}
        if isinstance(analysis, dict) and analysis.get("api_source") == "fallback":
            results["warnings"].append("Communication Agent: Using OpenAI-compatible fallback service (Gemini quota exhausted).")

        # 2. Friction Detection
        friction_results = friction_detection_agent.detect_communication_friction(f"communication_analysis_{message_id}")
        logger.debug("Friction detection results type: %s", type(friction_results))
        # Ensure proper JSON serialization - always return a dict, never a string
        friction_serialized = serialize_google_cloud_object(friction_results)
        logger.debug("After serialization, type: %s, is dict: %s", type(friction_serialized), isinstance(friction_serialized, dict))
        # Ensure it's a dict, not a string
        if isinstance(friction_serialized, str):
            logger.warning("Friction detection was serialized as string! Attempting to parse...")
            try:
                friction_serialized = json.loads(friction_serialized)
            except:
                logger.warning("JSON parse failed, trying Python literal eval")
                import ast
                try:
                    friction_serialized = ast.literal_eval(friction_serialized)
                except Exception as e:
                    logger.error("Failed to parse friction detection: %s", e)
                    friction_serialized = {"error": "Failed to parse friction detection", "raw": friction_serialized[:200]}
        if not isinstance(friction_serialized, dict):
            logger.error("Friction detection is not a dict after processing! Type: %s", type(friction_serialized))
            friction_serialized = {"error": "Invalid response format", "type": str(type(friction_serialized))}
        results["friction_detection"] = friction_serialized
        
        # Check for quota errors and API source in friction detection
        friction_str = json.dumps(friction_serialized) if isinstance(friction_serialized, dict) else str(friction_results)
        if "429" in friction_str or "RESOURCE_EXHAUSTED" in friction_str or "quota" in friction_str.lower():
            results["warnings"].append("Friction Detection Agent: Gemini API quota exceeded. Using fallback service.")
        # Check if using fallback service
        if isinstance(friction_serialized, dict) and friction_serialized.get("api_source") == "fallback":
            results["warnings"].append("Friction Detection Agent: Using OpenAI-compatible fallback service (Gemini quota exhausted).")

        # 3. Intervention Suggestion
        intervention_suggestion = intervention_agent.suggest_intervention(f"communication_analysis_{message_id}")
        logger.debug("Intervention suggestion results type: %s", type(intervention_suggestion))
        # Ensure proper JSON serialization - always return a dict, never a string
        intervention_serialized = serialize_google_cloud_object(intervention_suggestion)
        logger.debug("After serialization, type: %s, is dict: %s", type(intervention_serialized), isinstance(intervention_serialized, dict))
        # Ensure it's a dict, not a string
        if isinstance(intervention_serialized, str):
            logger.warning("Intervention suggestion was serialized as string! Attempting to parse...")
            try:
                intervention_serialized = json.loads(intervention_serialized)
            except:
                logger.warning("JSON parse failed, trying Python literal eval")
                import ast
                try:
                    intervention_serialized = ast.literal_eval(intervention_serialized)
                except Exception as e:
                    logger.error("Failed to parse intervention suggestion: %s", e)
                    intervention_serialized = {"error": "Failed to parse intervention suggestion", "raw": intervention_serialized[:200]}
        if not isinstance(intervention_serialized, dict):
            logger.error("Intervention suggestion is not a dict after processing! Type: %s", type(intervention_serialized))
            intervention_serialized = {"error": "Invalid response format", "type": str(type(intervention_serialized))}
        results["intervention_suggestion"] = intervention_serialized
        
        # Check for quota errors in intervention
        intervention_str = json.dumps(intervention_serialized) if isinstance(intervention_serialized, dict) else str(intervention_suggestion)
        if "429" in intervention_str or "RESOURCE_EXHAUSTED" in intervention_str or "quota" in intervention_str.lower():
            results["warnings"].append("Intervention Agent: Gemini API quota exceeded. Using fallback service.")

    except Exception as e:
        results["error"] = str(e)
        logger.exception("[API Error] %s", e)

    # Ensure all responses are JSON-serializable
    try:
        # Test serialization
        json.dumps(results)
    except (TypeError, ValueError) as e:
        logger.warning("Response contains non-serializable objects, attempting to fix: %s", e)
        # Convert any remaining non-serializable objects to strings
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                return str(obj)
        results = make_serializable(results)

    return jsonify(results)

if __name__ == '__main__':
    # It's recommended to run Flask in development mode for easier debugging.
    # For production, use a production-ready WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, host='0.0.0.0', port=5000, load_dotenv=False)

