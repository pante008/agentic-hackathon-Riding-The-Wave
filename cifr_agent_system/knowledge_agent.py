import os
from .config import Config # Import the Config class
from typing import Dict, Any

class KnowledgeAgent:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.knowledge_base: Dict[str, Any] = {}

    def store_context(self, key: str, value: Any):
        """Stores a piece of context in the knowledge base."""
        self.knowledge_base[key] = value
        print(f"KnowledgeAgent: Stored context for key '{key}'")

    def retrieve_context(self, key: str) -> Any:
        """Retrieves context from the knowledge base."""
        return self.knowledge_base.get(key)

    def search_knowledge(self, query: str) -> Dict[str, Any]:
        """Performs a basic search over the knowledge base (placeholder for advanced search)."""
        results = {}
        for key, value in self.knowledge_base.items():
            if query.lower() in str(key).lower() or query.lower() in str(value).lower():
                results[key] = value
        print(f"KnowledgeAgent: Searched for '{query}', found {len(results)} results.")
        return results

if __name__ == "__main__":
    # Removed direct os.getenv for project_id as it's handled by Config now
    if not Config.GCP_PROJECT_ID:
        print("Please set the GCP_PROJECT_ID environment variable in your .env file.")
    else:
        agent = KnowledgeAgent(project_id=Config.GCP_PROJECT_ID, location=Config.GCP_LOCATION)
        
        # Example Usage
        agent.store_context("project_scope", {"goal": "Reduce intercompany friction", "key_metrics": ["collaboration_efficiency", "issue_resolution_time"]})
        print(agent.retrieve_context("project_scope"))
        
        agent.update_context("project_scope", {"status": "in_progress"})
        print(agent.retrieve_context("project_scope"))
        
        agent.delete_context("project_scope")
        print(agent.retrieve_context("project_scope"))
