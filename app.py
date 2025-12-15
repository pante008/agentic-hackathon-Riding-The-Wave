import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import base64
import json

# Ensure environment variables are loaded for Config to access them
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Import agents and Config from your cifr_agent_system package
from cifr_agent_system.config import Config
from cifr_agent_system.communication_agent import CommunicationAgent
from cifr_agent_system.knowledge_agent import KnowledgeAgent
from cifr_agent_system.friction_detection_agent import FrictionDetectionAgent
from cifr_agent_system.intervention_agent import InterventionAgent
from cifr_agent_system.utils import generate_unique_id

def serialize_google_cloud_object(obj):
    """Recursively converts Google Cloud client library objects to JSON serializable types."""
    if hasattr(obj, '__dict__'):
        # Handle Google Cloud protobuf objects
        if hasattr(obj, '_pb'):
            return serialize_google_cloud_object(obj._pb)
        # Recursively process dictionary-like objects
        return {k: serialize_google_cloud_object(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    if isinstance(obj, (list, tuple)):
        # Recursively process lists/tuples
        return [serialize_google_cloud_object(elem) for elem in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
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

# Import agents and Config from your cifr_agent_system package
from cifr_agent_system.config import Config
from cifr_agent_system.communication_agent import CommunicationAgent
from cifr_agent_system.knowledge_agent import KnowledgeAgent
from cifr_agent_system.friction_detection_agent import FrictionDetectionAgent
from cifr_agent_system.intervention_agent import InterventionAgent
from cifr_agent_system.utils import generate_unique_id

app = Flask(__name__, 
            static_folder='./frontend/static',
            template_folder='./frontend/templates')

# Initialize agents globally or per-request if state management is complex
# For simplicity, we'll initialize them globally here.
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

    print(f"[API] Processing message ID: {message_id}")

    results = {
        "original_message": sample_message,
        "communication_analysis": None,
        "knowledge_update_status": None,
        "friction_detection": None,
        "intervention_suggestion": None,
        "error": None
    }

    try:
        # 1. Communication Agent processing
        comm_agent_results = communication_agent.process_collaboration_message(sample_message)
        results["communication_analysis"] = serialize_google_cloud_object(comm_agent_results)
        results["knowledge_update_status"] = "Context stored under 'communication_analysis_{}'".format(message_id)

        # 2. Friction Detection
        friction_results = friction_detection_agent.detect_communication_friction(f"communication_analysis_{message_id}")
        results["friction_detection"] = serialize_google_cloud_object(friction_results)

        # 3. Intervention Suggestion
        intervention_suggestion = intervention_agent.suggest_intervention(f"communication_analysis_{message_id}")
        results["intervention_suggestion"] = serialize_google_cloud_object(intervention_suggestion)

    except Exception as e:
        results["error"] = str(e)
        print(f"[API Error] {e}")

    return jsonify(results)

if __name__ == '__main__':
    # It's recommended to run Flask in development mode for easier debugging.
    # For production, use a production-ready WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, host='0.0.0.0', port=5000)

