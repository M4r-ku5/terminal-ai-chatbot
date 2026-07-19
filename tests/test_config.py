import os
import json
import tempfile
from src.terminal_ai_chatbot.config import load_config, save_config
from src.terminal_ai_chatbot.tokens import estimate_tokens

def test_load_config_defaults():
    """Test loading config when file does not exist returns defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            config = load_config()
            assert config["model"] == "nvidia/nemotron-3-nano-30b-a3b:free"
            assert config["history_length"] == 20
            assert config["auto_compact"] is False
        finally:
            os.chdir(old_cwd)

def test_load_config_from_file():
    """Test loading config from existing file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        test_config = {
            "model": "test/model",
            "history_length": 10,
            "auto_compact": True
        }
        with open(config_path, "w") as f:
            json.dump(test_config, f)
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            config = load_config()
            assert config["model"] == "test/model"
            assert config["history_length"] == 10
            assert config["auto_compact"] is True
        finally:
            os.chdir(old_cwd)

def test_load_config_missing_keys():
    """Test loading config with missing keys fills defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        with open(config_path, "w") as f:
            json.dump({"model": "custom/model"}, f)
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            config = load_config()
            assert config["model"] == "custom/model"
            assert config["history_length"] == 20
            assert config["auto_compact"] is False
        finally:
            os.chdir(old_cwd)

def test_save_config():
    """Test saving config to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        test_config = {
            "model": "test/model",
            "history_length": 5,
            "auto_compact": True
        }
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            save_config(test_config)
            with open(config_path, "r") as f:
                saved = json.load(f)
            assert saved == test_config
        finally:
            os.chdir(old_cwd)

def test_estimate_tokens_string():
    """Test token estimation from string."""
    text = "Hello world"
    tokens = estimate_tokens(text)
    assert tokens == max(1, len(text) // 4)

def test_estimate_tokens_int():
    """Test token estimation from int (char count)."""
    chars = 100
    tokens = estimate_tokens(chars)
    assert tokens == chars // 4

def test_estimate_tokens_minimum():
    """Test minimum token count is 1."""
    tokens = estimate_tokens("")
    assert tokens == 1
    tokens = estimate_tokens("a")
    assert tokens == 1
