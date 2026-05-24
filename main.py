import os
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY");
if not API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found.");
    exit(1);

user_message = input("You: ");

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "arcee-ai/trinity-large-thinking:free",
        "messages": [
            {"role": "user", "content" : user_message}
        ]
    }
);

if response.status_code != 200:
    print(f"API ERROR: {response.status_code}");
    print(response.text);
    exit(1);

data = response.json();
ai_message = data["choices"][0]["message"]["content"];
print(f"AI: {ai_message}");