import os


def get_config() -> dict:
    return {
        "project_endpoint": os.environ.get("PROJECT_ENDPOINT", ""),
        "model_deployment_name": os.environ.get("MODEL_DEPLOYMENT_NAME", "agent-model"),
        "backend_url": os.environ.get("BACKEND_URL", "http://localhost:8000"),
    }
