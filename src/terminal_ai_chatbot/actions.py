import os
from .config import load_config, save_config
from .chat_logic import list_chat_files, load_chat_messages, save_chat
from .settings import SettingsScreen
from .models_cache import load_cached_models
from .api import call_api, fetch_and_update_model_info
from .tokens import update_model_indicator
from textual.widgets import Static, ListView, ListItem, Label, RichLog
from datetime import datetime


def on_mount(app) -> None:
    """Initialize the app state when the app is mounted."""
        
    os.makedirs("chats", exist_ok=True)
    app.config = load_config()
    app.current_chat_file = None
    app.messages = []
    populate_chat_list(app)
    app.title = "Terminal AI Chatbot"
    app.query_one("#model-indicator", Static).update(f"Model: {app.config['model']}")
    app.run_worker(fetch_and_update_model_info(app))


def populate_chat_list(app):
        """Populate the chat list in the sidebar with available chat files."""

        chat_list = app.query_one("#chat-list", ListView)
        chat_list.clear()

        for filename in list_chat_files():
            safe_id = filename.replace(".json", "")
            item = ListItem(Label(filename), id=safe_id)
            item.filename = filename
            chat_list.append(item)
    

def action_load_chat(app):
    """Load the selected chat from the list and display it in the message log."""

    chat_list = app.query_one("#chat-list", ListView)

    if chat_list.highlighted_child:
        safe_id = chat_list.highlighted_child.id
        filename = safe_id + ".json"
        filepath = os.path.join("chats", filename)
        messages = load_chat_messages(filepath)

        if messages:
            message_log = app.query_one("#message-log", RichLog)
            message_log.clear()

            app.messages = messages[:]
            app.current_chat_file = filepath
            update_model_indicator(app)


            # Default value for history_length is 20 if not specified in config
            history_len = app.config.get("history_length", 20)
            if history_len > 0:
                messages = messages[-history_len:]

            for message in messages:
                role = message["role"]
                content = message["content"].lstrip('\n')

                if role == "user":
                    message_log.write(f"[bold cyan]You:[/bold cyan] {content}\n")
                else:
                    message_log.write(f"[bold green]AI:[/bold green] {content}\n")

        else:
            app.notify("Loading error.", severity="error")


def action_settings(app) -> None:
    """Open settings screen."""

    cached_models = load_cached_models()
    models = list(cached_models.keys()) if cached_models else [app.config["model"]]

    def handle_result(config: dict | None) -> None:
        if config is not None:
            app.config = config
            save_config(config)
            update_model_indicator(app)
            app.notify("Settings saved.", severity="success")
    
    # 'callback=handle_result' defines the function to call when the settings screen is closed
    app.push_screen(SettingsScreen(app.config, models), callback=handle_result)


def action_new_chat(app): 
    """Clears the current chat and starts a new one."""

    message_log = app.query_one("#message-log", RichLog)
    message_log.clear()
    app.current_chat_file = None
    app.messages = []
    update_model_indicator(app)
    app.notify("New chat started. Type your message to begin.")


async def on_input_submitted(app, event):
    """Handle user input submission."""

    # strip() removes leading and trailing whitespace, including newlines
    user_message = event.value.strip()
    if user_message == "":
        return

    event.input.clear()
    app.messages.append({"role": "user", "content": user_message})
    
    output_log = app.query_one("#message-log", RichLog)
    output_log.write(f"[bold cyan]You:[/bold cyan] {user_message}\n")

    if app.current_chat_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        app.current_chat_file = os.path.join("chats", f"chat_{timestamp}.json")

    # API call
    try:
        response = await call_api(app.messages, app.config)
        ai_message = response["choices"][0]["message"]["content"]
        
        app.messages.append({"role": "assistant", "content": ai_message})
        output_log.write(f"[bold green]AI:[/bold green] {ai_message}\n")
        save_chat(app.messages, app.current_chat_file)
        output_log.scroll_end()
        update_model_indicator(app)

    except Exception as e:
        # If the last message was from the user, remove it to avoid sending it again on retry
        if app.messages and app.messages[-1]["role"] == "user":
            app.messages.pop()

        output_log.write(f"[bold red]Errore:[/bold red] {e}\n")
        app.notify(f"Errore API: {e}", severity="error")