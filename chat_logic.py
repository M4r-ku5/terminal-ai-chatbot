import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from config import load_config


# Load environment variables from .env file
load_dotenv()

# Get the OpenRouter API key from environment variables
API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found.")
    exit(1)


def chat(initial_messages=None, filename=None, config=None):
    """Chat loop, handles chat save in local memory and AI request/response."""

    if config is None:
        config = load_config()

    messages = [] if initial_messages is None else list(initial_messages)

    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"chats/chat_{timestamp}.json"

    # Prints the previous messages
    if messages:

        if config["history_length"] > 0:
            last_messages = messages[-config["history_length"]:]
        else:
            last_messages = []


        for m in last_messages:

            # Prevents newline after AI label
            content = m["content"].lstrip('\n')
            if m["role"] == "user":
                 print(f"You: {content}")
            else:
                print(f"AI: {content}")
            
    # Chat loop
    while True:
        user_message = input("You ('/exit' to quit): ")
        if user_message == "/exit":
            break

        messages.append({"role": "user", "content": user_message})
        save_chat(messages, filename)

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": config["model"],
                "messages": messages
            }
        )

        if response.status_code != 200:
            print(f"API ERROR: {response.status_code}")
            print(response.text)
            exit(1)

        data = response.json()
        ai_message = data["choices"][0]["message"]["content"]
        print(f"AI: {ai_message}")

        messages.append({"role": "assistant", "content": ai_message})
        save_chat(messages, filename)


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