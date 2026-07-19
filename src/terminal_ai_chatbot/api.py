import os
import requests
import asyncio
from .models_cache import get_model_context_length
from .tokens import update_model_indicator
from dotenv import load_dotenv



load_dotenv()

async def fetch_and_update_model_info(app) -> None:
    """Fetch model context length and update the UI indicator."""

    model_id = app.config.get("model", "")
    max_tokens = get_model_context_length(model_id)
    app._max_tokens = max_tokens

    if max_tokens:
        update_model_indicator(app, max_tokens)


async def call_api(messages, config):
    """Call the OpenRouter API asynchronously to not block the UI."""

    loop = asyncio.get_event_loop()

    def _sync_call():
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": config["model"],
                "messages": messages
            },
            # Timeout to prevent hanging indefinitely if the API is unresponsive
            timeout=30
        )
        return response

    # Run the synchronous API call in a separate thread to avoid blocking the main event loop
    # None means using the default ThreadPoolExecutor
    response = await loop.run_in_executor(None, _sync_call)
    
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
    
    return response.json()