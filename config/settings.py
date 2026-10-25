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

    # Deployment
    cors_origins: str = (
        "http://localhost:8501,http://127.0.0.1:8501,"
        "http://localhost:3000,http://127.0.0.1:3000"
    )
    enforce_api_key: bool = False

    # LLM Model Names
    orchestrator_model: str = "nvidia/nemotron-3.5-lightning:free"
    synthesis_model: str = "nvidia/nemotron-3.5-lightning:free"
    rag_model: str = "nvidia/nemotron-3.5-lightning:free"
    chatbot_model: str = "nvidia/nemotron-3.5-lightning:free"

    # OmniRoute Gateway Settings (Local / Remote multi-provider proxy)
    omniroute_base_url: str = "http://localhost:20128/v1"
    omniroute_api_key: str = "omniroute-local"
    omniroute_model: str = "antigravity/gemini-3.8-flash-medium"
    use_omniroute: bool = True

    # Vision Model
    vision_model_name: str = "resnet50"
    num_disease_classes: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origin_list(self) -> list[str]:
        """Allowed browser origins parsed from the comma-separated setting."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()


settings = get_settings()
