import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get("OPENROUTER_API_KEY");
if not API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found.");
    exit(1);

messages = []

while True:
    user_message = input("You ('/exit' to quit): ");
    if user_message == "/exit":
        break

    messages.append({"role": "user", "content": user_message})

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "arcee-ai/trinity-mini",
            "messages": messages
        }
    );

    if response.status_code != 200:
        print(f"API ERROR: {response.status_code}");
        print(response.text);
        exit(1);

    data = response.json();
    ai_message = data["choices"][0]["message"]["content"];
    print(f"AI: {ai_message}");

    messages.append({"role": "assistant", "content": ai_message})