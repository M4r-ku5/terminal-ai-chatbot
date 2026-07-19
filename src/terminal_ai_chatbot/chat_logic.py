import os
import json



def save_chat(messages, filepath):
    """Save the messages list to a JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n[ERROR] Failed to save chat: {e}")


def load_chat_messages(filepath):
    """Load messages from a JSON file. Return list of messages, or None on error."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"\n[ERROR] Could not load chat '{filepath}': {e}")
        return None


def list_chat_files():
    """Return a sorted list of .json filenames in the chats directory."""
    if not os.path.isdir("chats"):
        return []
    files = [f for f in os.listdir("chats") if f.endswith(".json")]
    return sorted(files, reverse=True)