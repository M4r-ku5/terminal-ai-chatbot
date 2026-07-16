import json
import os
import time
from pathlib import Path
from typing import Optional
import requests



CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "models_cache.json"
CACHE_EXPIRATION_HOURS = 24
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
REQUEST_TIMEOUT_SECONDS = 10



def _ensure_cache_dir_exists():
    """Ensure that the cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_cached_models() -> Optional[dict]:
    """Load cached models from the cache file if it exists and is not expired."""
    
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        
        timestamp = cache_data.get("timestamp", 0)
        age_hours = (time.time() - timestamp) / 3600
        if age_hours > CACHE_EXPIRATION_HOURS:
            return None
        
        return cache_data.get("models", {})

    except (json.JSONDecodeError, OSError, KeyError):
        return None
    

def save_cached_models(models: dict) -> None:
    """Save models to the cache file with the current timestamp."""
        
    _ensure_cache_dir_exists()
    cache_data = {
        "timestamp": time.time(),
        "models": models
    }
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except OSError:
        # If saving fails, simply ignore it
        pass


def fetch_models_from_openrouter() -> Optional[dict]:
    """Fetch the list of models from OpenRouter API."""
        
    try:
        response = requests.get(
            OPENROUTER_MODELS_URL,
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()

        models = {}
        for model in data.get("data", []):
            model_id = model.get("id")
            context_length = model.get("context_length")
            if model_id and context_length:
                models[model_id] = context_length
            
        return models if models else None
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return None
        

def get_model_context_length(model_id: str) -> Optional[int]:
    """Get the context length for a specific model, using cache if available."""
        
    # Try cache first
    cached_models = load_cached_models()
    if cached_models and model_id in cached_models:
        return cached_models[model_id]
        
    # Cache miss or expired: fetch from OpenRouter
    models = fetch_models_from_openrouter()
    if models:
        save_cached_models(models)
        return models.get(model_id)
        
    return None