import os
import json
import time
import tempfile
from unittest.mock import patch, MagicMock
from src.terminal_ai_chatbot.models_cache import (
    load_cached_models,
    save_cached_models,
    fetch_models_from_openrouter,
    get_model_context_length,
    CACHE_DIR,
    CACHE_FILE,
    CACHE_EXPIRATION_HOURS,
)


def test_load_cached_models_no_file():
    """Test loading cache when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            result = load_cached_models()
            assert result is None
        finally:
            os.chdir(old_cwd)


def test_load_cached_models_valid():
    """Test loading valid cache file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            # Create cache directory and file
            os.makedirs("cache", exist_ok=True)
            cache_data = {
                "timestamp": time.time(),
                "models": {"model1": 4096, "model2": 8192}
            }
            with open("cache/models_cache.json", "w") as f:
                json.dump(cache_data, f)
            
            result = load_cached_models()
            assert result == {"model1": 4096, "model2": 8192}
        finally:
            os.chdir(old_cwd)


def test_load_cached_models_expired():
    """Test loading expired cache returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            os.makedirs("cache", exist_ok=True)
            # Old timestamp (25 hours ago)
            cache_data = {
                "timestamp": time.time() - (25 * 3600),
                "models": {"model1": 4096}
            }
            with open("cache/models_cache.json", "w") as f:
                json.dump(cache_data, f)
            
            result = load_cached_models()
            assert result is None
        finally:
            os.chdir(old_cwd)


def test_load_cached_models_invalid_json():
    """Test loading invalid JSON returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            os.makedirs("cache", exist_ok=True)
            with open("cache/models_cache.json", "w") as f:
                f.write("not valid json")
            
            result = load_cached_models()
            assert result is None
        finally:
            os.chdir(old_cwd)


def test_save_cached_models():
    """Test saving models to cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            models = {"model1": 4096, "model2": 8192}
            save_cached_models(models)
            
            # Verify file was created and contains correct data
            assert os.path.exists("cache/models_cache.json")
            with open("cache/models_cache.json", "r") as f:
                cache_data = json.load(f)
            
            assert "timestamp" in cache_data
            assert cache_data["models"] == models
            assert cache_data["timestamp"] <= time.time()
        finally:
            os.chdir(old_cwd)


@patch("src.terminal_ai_chatbot.models_cache.requests.get")
def test_fetch_models_from_openrouter_success(mock_get):
    """Test successful fetch from OpenRouter API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": "model1", "context_length": 4096},
            {"id": "model2", "context_length": 8192},
            {"id": "model3"},  # Missing context_length - should be skipped
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = fetch_models_from_openrouter()
    
    assert result == {"model1": 4096, "model2": 8192}
    mock_get.assert_called_once()


@patch("src.terminal_ai_chatbot.models_cache.requests.get")
def test_fetch_models_from_openrouter_failure(mock_get):
    """Test fetch failure returns None."""
    import requests
    mock_get.side_effect = requests.RequestException("Network error")
    
    result = fetch_models_from_openrouter()
    
    assert result is None


@patch("src.terminal_ai_chatbot.models_cache.requests.get")
def test_fetch_models_from_openrouter_invalid_json(mock_get):
    """Test fetch with invalid JSON returns None."""
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = fetch_models_from_openrouter()
    
    assert result is None


@patch("src.terminal_ai_chatbot.models_cache.fetch_models_from_openrouter")
@patch("src.terminal_ai_chatbot.models_cache.load_cached_models")
@patch("src.terminal_ai_chatbot.models_cache.save_cached_models")
def test_get_model_context_length_from_cache(mock_save, mock_load, mock_fetch):
    """Test getting context length from cache."""
    mock_load.return_value = {"cached_model": 4096}
    
    result = get_model_context_length("cached_model")
    
    assert result == 4096
    mock_load.assert_called_once()
    mock_fetch.assert_not_called()
    mock_save.assert_not_called()


@patch("src.terminal_ai_chatbot.models_cache.fetch_models_from_openrouter")
@patch("src.terminal_ai_chatbot.models_cache.load_cached_models")
@patch("src.terminal_ai_chatbot.models_cache.save_cached_models")
def test_get_model_context_length_fetch_and_cache(mock_save, mock_load, mock_fetch):
    """Test getting context length by fetching and caching."""
    mock_load.return_value = None  # Cache miss
    mock_fetch.return_value = {"fetched_model": 8192}
    
    result = get_model_context_length("fetched_model")
    
    assert result == 8192
    mock_load.assert_called_once()
    mock_fetch.assert_called_once()
    mock_save.assert_called_once_with({"fetched_model": 8192})


@patch("src.terminal_ai_chatbot.models_cache.fetch_models_from_openrouter")
@patch("src.terminal_ai_chatbot.models_cache.load_cached_models")
def test_get_model_context_length_not_found(mock_load, mock_fetch):
    """Test getting context length for unknown model."""
    mock_load.return_value = None
    mock_fetch.return_value = {"other_model": 4096}
    
    result = get_model_context_length("unknown_model")
    
    assert result is None