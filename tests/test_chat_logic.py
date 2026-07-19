import os
import json
import tempfile
from src.terminal_ai_chatbot.chat_logic import save_chat, load_chat_messages, list_chat_files


def test_save_chat():
    """Test saving chat messages to JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_chat.json")
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        save_chat(messages, filepath)
        
        with open(filepath, "r") as f:
            saved = json.load(f)
        assert saved == messages


def test_load_chat_messages():
    """Test loading chat messages from JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_chat.json")
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        with open(filepath, "w") as f:
            json.dump(messages, f)
        
        loaded = load_chat_messages(filepath)
        assert loaded == messages


def test_load_chat_messages_not_found():
    """Test loading non-existent file returns None."""
    result = load_chat_messages("/nonexistent/path/chat.json")
    assert result is None


def test_load_chat_messages_invalid_json():
    """Test loading invalid JSON returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "invalid.json")
        with open(filepath, "w") as f:
            f.write("not valid json")
        
        result = load_chat_messages(filepath)
        assert result is None


def test_list_chat_files():
    """Test listing chat files in directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create chats subdirectory
        chats_dir = os.path.join(tmpdir, "chats")
        os.makedirs(chats_dir)
        
        # Create some chat files
        for name in ["chat_1.json", "chat_2.json", "chat_3.json"]:
            with open(os.path.join(chats_dir, name), "w") as f:
                json.dump([], f)
        
        # Create a non-json file (should be ignored)
        with open(os.path.join(chats_dir, "readme.txt"), "w") as f:
            f.write("ignore me")
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            files = list_chat_files()
            assert len(files) == 3
            assert "chat_1.json" in files
            assert "chat_2.json" in files
            assert "chat_3.json" in files
            assert "readme.txt" not in files
        finally:
            os.chdir(old_cwd)


def test_list_chat_files_empty():
    """Test listing chat files when directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            files = list_chat_files()
            assert files == []
        finally:
            os.chdir(old_cwd)