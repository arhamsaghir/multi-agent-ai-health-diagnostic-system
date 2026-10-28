"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import secrets
import sys
import os
from pathlib import Path

from config import settings

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level.upper(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
)
os.makedirs("logs", exist_ok=True)
logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="1 day", retention="30 days")

def _is_production() -> bool:
    """True when the service is running with production settings.

    Read live from settings rather than frozen at import time, so the
    startup guard and the request path always agree on the environment.
    """
    return settings.app_env.lower() in {"production", "prod"}


# The docs surface is fixed when the app object is built.
_IS_PRODUCTION = _is_production()

app = FastAPI(
    title="Multi-Agent AI Health Diagnostic System",
    description="B.Tech Final Year Project — AI-powered medical diagnosis using multi-agent orchestration",
    version="0.1.0",
    # Interactive API docs are development conveniences; they are not exposed
    # in production deployments.
    docs_url=None if _IS_PRODUCTION else "/docs",
    redoc_url=None if _IS_PRODUCTION else "/redoc",
    openapi_url=None if _IS_PRODUCTION else "/openapi.json",
)

# CORS — allowed origins are deployment-configurable via CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# API Key Authentication Middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Validate the API key for non-public endpoints.

    Enforcement is on by default. The unauthenticated bypass exists only in
    development and only while ``ALLOW_INSECURE_DEV`` is enabled; production
    startup refuses to run without a configured secret.
    """
    # Public endpoints that don't require authentication
    public_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
    if any(request.url.path.startswith(p) for p in public_paths):
        return await call_next(request)

    # Explicit, development-only bypass
    if settings.app_env == "development" and settings.allow_insecure_dev:
        return await call_next(request)

    api_key = request.headers.get("X-API-Key") or ""
    if not api_key or not secrets.compare_digest(api_key, settings.secret_key):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized. Provide X-API-Key header."}
        )

    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    """Validate environment, check API keys, verify model files."""
    logger.info("=" * 60)
    logger.info("Starting Multi-Agent AI Health Diagnostic System v0.1.0")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info("=" * 60)

    # Fail fast rather than serving an unauthenticated clinical API
    if _is_production():
        if not settings.enforce_api_key:
            raise RuntimeError("ENFORCE_API_KEY must remain enabled outside development")
        if not settings.secret_key:
            raise RuntimeError("SECRET_KEY must be set outside development")
        logger.info("API key authentication: enforced")
    elif settings.allow_insecure_dev:
        logger.warning("API key authentication: disabled (development bypass)")

    # Check API keys
    if not settings.openrouter_api_key and not os.environ.get("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY not set — LLM synthesis features will fail")
    else:
        logger.info("OpenRouter API key: configured")
    
    if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set — Voice transcription will be unavailable")
    else:
        logger.info("OpenAI API key: configured (Whisper)")
    
    if not settings.google_api_key and not os.environ.get("GOOGLE_API_KEY"):
        logger.warning("GOOGLE_API_KEY not set — Gemini synthesis will fail")
    else:
        logger.info("Google API key: configured (Gemini)")
    
    # Verify model files
    model_checks = [
        (settings.vision_model_path, "Vision model"),
        (settings.prediction_model_path.replace(".pkl", "_metadata.json"), "Prediction model metadata"),
        (settings.vector_store_dir + "/medical_knowledge.faiss", "FAISS vector store"),
    ]
    
    for path, desc in model_checks:
        if os.path.exists(path):
            size = os.path.getsize(path)
            logger.info(f"Model file verified: {desc} ({size:,} bytes)")
        else:
            logger.warning(f"Model file missing: {desc} ({path})")
    
    # Verify directories
    required_dirs = ["data", "models", "logs", "frontend"]
    for d in required_dirs:
        if os.path.exists(d):
            logger.debug(f"Directory exists: {d}/")
        else:
            logger.warning(f"Directory missing: {d}/")
            os.makedirs(d, exist_ok=True)
    
    # Verify database directory
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Startup validation complete — system ready")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log system shutdown event for audit and debugging."""
    logger.info("Shutting down system")


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status."""
    import time
    start = time.time()
    
    status = {
        "status": "healthy",
        "environment": settings.app_env,
        "version": "0.1.0",
        "authentication": (
            "open (development bypass)"
            if settings.app_env == "development" and settings.allow_insecure_dev
            else "enforced"
        ),
    }

    # Check model file availability
    model_status = {}
    if os.path.exists(settings.vision_model_path):
        model_status["vision"] = "loaded"
    else:
        model_status["vision"] = "missing"

    pred_metadata = settings.prediction_model_path.replace(".pkl", "_metadata.json")
    if os.path.exists(pred_metadata):
        model_status["prediction"] = "loaded"
    else:
        model_status["prediction"] = "missing"

    faiss_path = settings.vector_store_dir + "/medical_knowledge.faiss"
    if os.path.exists(faiss_path):
        model_status["rag"] = "loaded"
    else:
        model_status["rag"] = "missing"

    status["models"] = model_status

    # Agent availability reflects what is actually usable in this deployment
    llm_configured = bool(settings.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY"))
    voice_configured = bool(settings.openai_api_key or os.environ.get("OPENAI_API_KEY"))
    status["agents"] = {
        "orchestrator": "active",
        "nlp": "pattern_extractor + ner_model" if settings.enable_biobert_ner else "pattern_extractor",
        "vision": model_status["vision"],
        "rag": model_status["rag"],
        "prediction": model_status["prediction"],
        "voice": "configured" if voice_configured else "unavailable",
        "synthesis": "llm_configured" if llm_configured else "rule_based_fallback",
    }
    status["response_time_ms"] = round((time.time() - start) * 1000, 2)
    
    return status


# Import routes
from src.api.routes import diagnosis, chat, vision, history, stream, report, fhir
app.include_router(diagnosis.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(vision.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(fhir.router, prefix="/api")
