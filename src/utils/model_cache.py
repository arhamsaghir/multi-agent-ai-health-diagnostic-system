"""Model cache manager for lazy-loading heavy ML models.

Prevents OOM crashes by loading models on-demand and tracking references.
Heavy models (BioBERT, ResNet, embedding models) are only loaded when
first needed, not at application startup.
"""

from typing import Any, Optional
import threading
from loguru import logger


class ModelCache:
    """Thread-safe cache for ML models with lazy loading.
    
    Models are loaded on first access and kept in memory until explicitly
    unloaded. Reference counting prevents premature unloading.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._models: dict[str, Any] = {}
        self._ref_counts: dict[str, int] = {}
        self._load_funcs: dict[str, callable] = {}
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("ModelCache initialized")
    
    def register(self, name: str, load_func: callable):
        """Register a model with its loading function.
        
        Args:
            name: Unique model identifier.
            load_func: Callable that returns the loaded model.
        """
        with self._lock:
            self._load_funcs[name] = load_func
            self._ref_counts[name] = 0
            logger.debug(f"Registered model: {name}")
    
    def get(self, name: str) -> Any:
        """Get a model, loading it if necessary.
        
        Args:
            name: Model identifier.
            
        Returns:
            The loaded model instance.
        """
        with self._lock:
            if name not in self._load_funcs:
                raise KeyError(f"Model '{name}' not registered")
            
            # Increment reference count
            self._ref_counts[name] = self._ref_counts.get(name, 0) + 1
            
            # Load if not already cached
            if name not in self._models:
                logger.info(f"Loading model: {name}")
                try:
                    self._models[name] = self._load_funcs[name]()
                    logger.info(f"Model loaded: {name}")
                except Exception as e:
                    self._ref_counts[name] = max(0, self._ref_counts[name] - 1)
                    logger.error(f"Failed to load model '{name}': {e}")
                    raise
            
            return self._models[name]
    
    def release(self, name: str):
        """Release a reference to a model.
        
        When reference count reaches 0, the model is unloaded to free memory.
        
        Args:
            name: Model identifier.
        """
        with self._lock:
            if name in self._ref_counts:
                self._ref_counts[name] = max(0, self._ref_counts[name] - 1)
                if self._ref_counts[name] == 0 and name in self._models:
                    logger.info(f"Unloading model: {name}")
                    del self._models[name]
                    logger.info(f"Model unloaded: {name}")
    
    def is_loaded(self, name: str) -> bool:
        """Check if a model is currently loaded."""
        return name in self._models
    
    def get_status(self) -> dict:
        """Get cache status information."""
        return {
            "loaded_models": list(self._models.keys()),
            "reference_counts": dict(self._ref_counts),
            "registered_models": list(self._load_funcs.keys()),
        }
    
    def unload_all(self):
        """Unload all models to free memory."""
        with self._lock:
            names = list(self._models.keys())
            for name in names:
                logger.info(f"Unloading model: {name}")
                del self._models[name]
            logger.info(f"Unloaded {len(names)} models")


# Global instance
model_cache = ModelCache()
