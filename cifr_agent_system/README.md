# Collaborative Intelligence & Friction Reduction (CIFR) Agent System

This project implements a multi-agent AI system designed to reduce intercompany friction in collaborations, leveraging Google Cloud Platform (GCP) and Gemini's multimodal reasoning capabilities.

## Getting Started

### 1. GCP Project Setup

1.  **Create a GCP Project:** If you don't have one, create a new project in the Google Cloud Console.
2.  **Enable APIs:** Enable the following APIs in your GCP project:
    *   **Vertex AI API**
    *   **Cloud DLP API**
    *   **Cloud Pub/Sub API**
    *   **Cloud Storage API**
    *   **Cloud Natural Language API**
3.  **Authentication:**
    *   **Google AI API Key:** For Gemini API access, you need a Google AI API key.
        - Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new API key.
        - Copy the API key (it will look like: `AIzaSy...`).
    *   **Environment Variables:** Create a `.env` file in the root of the project (`/Users/epant/Desktop/Hackathon/`) with the following content:
         ```bash
         GCP_PROJECT_ID=your-gcp-project-id
         GOOGLE_API_KEY=your-google-ai-api-key
         ```
        Replace `your-gcp-project-id` with your actual GCP project ID and `your-google-ai-api-key` with your Google AI API key.
        Ensure you have `python-dotenv` installed (`pip install python-dotenv`) to load these variables.

### 2. Local Environment Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd cifr_agent_system
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Run the Main Application

To run the main orchestration script, navigate to the root of the project (`/Users/epant/Desktop/Hackathon/`) and execute it as a module:
```bash
python -m cifr_agent_system.main
```

### 4. Run the Web UI

To start the Flask web server for the UI, navigate to the project root (`/Users/epant/Desktop/Hackathon/`) and run the `app.py` file:
```bash
export FLASK_APP=app.py
flask run
```
Then, open your web browser and go to `http://127.0.0.1:5000/`.

## Project Structure

*   `communication_agent.py`: Handles communication monitoring and sentiment analysis.
*   `knowledge_agent.py`: Manages project knowledge and context.
*   `friction_detection_agent.py`: Detects misalignments and conflicts.
*   `intervention_agent.py`: Provides proactive suggestions and facilitates decisions.
*   `main.py`: Orchestrates agent interactions.
*   `config.py`: Configuration settings.
*   `utils.py`: Utility functions.

## How it Works (High-Level)

The system operates as a network of intelligent agents. Each agent has a specialized role in monitoring collaboration data, identifying friction points, and facilitating smoother intercompany interactions. Gemini's multimodal capabilities are leveraged for deep understanding of diverse content (text, images, diagrams) within communications and shared documents. Automated reasoning helps agents diagnose issues and propose intelligent interventions.

## MVP Focus for Hackathon

*   **Communication Channels:** Basic integration with a simulated chat/email stream.
*   **Friction Type:** Focusing on simple miscommunication detection and action item tracking.
*   **Multimodal:** Demonstrating Gemini's ability to interpret text and basic image/diagram context.
*   **Agent Interaction:** A clear flow between the Communication Agent, Knowledge Agent, and Intervention Agent for a specific scenario.

---
