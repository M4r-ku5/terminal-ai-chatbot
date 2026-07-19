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


def delete_chat_file(filename):
    """Delete a chat file from the chats directory."""
    filepath = os.path.join("chats", filename)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"\n[ERROR] Could not delete chat '{filename}': {e}")
        return False
    

def rename_chat_file(old_filename, new_filename):
    """Rename a chat file in the chats directory."""
        
    if not new_filename.endswith(".json"):
        new_filename += ".json"
        
    old_filepath = os.path.join("chats", old_filename)
    new_filepath = os.path.join("chats", new_filename)

    try:
        # Old file must exist and new file must not exist to proceed with renaming
        if not os.path.exists(old_filepath) or os.path.exists(new_filepath):
            return False
        os.rename(old_filepath, new_filepath)
        return True
    except Exception as e:
        print(f"\n[ERROR] Could not rename chat '{old_filename}' to '{new_filename}': {e}")
        return False