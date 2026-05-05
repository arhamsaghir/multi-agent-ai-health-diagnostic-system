"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the entire application."""

    # App
    app_env: str = "development"
    log_level: str = "debug"
    secret_key: str = "dev-secret-change-me"

    # LLM APIs
    openai_api_key: str = ""
    google_api_key: str = ""
    openrouter_api_key: str = ""
    nvidia_api_key: str = ""
    hf_token: str = ""

    # Database
    database_url: str = "sqlite:///./data/diagnostic.db"

    # Vector Store
    vector_store_dir: str = "./data/vector_store"

    # Model Paths
    vision_model_path: str = "./models/vision_resnet50.pth"
    prediction_model_path: str = "./models/prediction_xgboost.pkl"

    # API Endpoints
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    openai_base_url: str = "https://api.openai.com/v1"

    # LLM Model Names
    orchestrator_model: str = "openai/gpt-oss-120b:free"
    synthesis_model: str = "nvidia/nemotron-3-super-120b-a12b:free"
    rag_model: str = "nvidia/nemotron-3-super-120b-a12b:free"
    chatbot_model: str = "openai/gpt-oss-120b:free"

    # Vision Model
    vision_model_name: str = "resnet50"
    num_disease_classes: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()


settings = get_settings()
