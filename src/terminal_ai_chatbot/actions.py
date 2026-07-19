import os
from .config import load_config, save_config
from .chat_logic import list_chat_files, load_chat_messages, save_chat
from .settings import SettingsScreen
from .models_cache import load_cached_models
from .api import call_api, fetch_and_update_model_info
from .tokens import update_model_indicator
from .widgets import ConfirmScreen, InputScreen
from textual.widgets import Static, ListView, ListItem, Label, RichLog
from datetime import datetime
import textwrap


def on_mount(app) -> None:
    """Initialize the app state when the app is mounted."""
        
    os.makedirs("chats", exist_ok=True)
    app.config = load_config()
    app.current_chat_file = None
    app.messages = []
    app.run_worker(populate_chat_list(app))
    app.title = "Terminal AI Chatbot"
    app.query_one("#model-indicator", Static).update(f"Model: {app.config['model']}")
    app.run_worker(fetch_and_update_model_info(app))


def wrap_for_long(text: str, width: int = 100) -> str:
    """Wrap long lines for RichLog display."""

    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        if len(line) > width:
            wrapped_lines.extend(textwrap.wrap(line, width=width, break_long_words=True, break_on_hyphens=False))
        else:
            wrapped_lines.append(line)
    return '\n'.join(wrapped_lines)


async def populate_chat_list(app):
        """Populate the chat list in the sidebar with available chat files."""

        chat_list = app.query_one("#chat-list", ListView)
        await chat_list.clear()

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
                    message_log.write(f"[bold cyan]You:[/bold cyan] {wrap_for_long(content)}\n")
                else:
                    message_log.write(f"[bold green]AI:[/bold green] {wrap_for_long(content)}\n")

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


def action_delete_chat(app):
    """Delete the selected chat file from the chats directory."""

    chat_list = app.query_one("#chat-list", ListView)

    if not chat_list.highlighted_child:
        app.notify("No chat selected for deletion.", severity="error")
        return

    filename = chat_list.highlighted_child.filename


    def confirm_deletion(confirmed: bool) -> None:
        if confirmed:
            from .chat_logic import delete_chat_file
            if delete_chat_file(filename):
                app.notify(f"Deleted chat '{filename}'.", severity="success")
                app.run_worker(populate_chat_list(app))
                if app.current_chat_file and app.current_chat_file.endswith(filename):
                    action_new_chat(app)
            else:
                app.notify(f"Failed to delete chat '{filename}'.", severity="error")

    app.push_screen(ConfirmScreen(f"Are you sure you want to delete '{filename}'?"), callback=confirm_deletion)


def action_rename_chat(app):
    """Rename the selected chat file in the chats directory."""

    chat_list = app.query_one("#chat-list", ListView)

    if not chat_list.highlighted_child:
        app.notify("No chat selected for renaming.", severity="error")
        return
    
    old_filename = chat_list.highlighted_child.filename

    def handle_rename(new_filename: str | None) -> None:
        # Checks if the new filename is not None and not just whitespace
        if new_filename and new_filename.strip():
            new_filename = new_filename.strip()
            if not new_filename.endswith(".json"):
                new_filename += ".json"

            from .chat_logic import rename_chat_file
            if rename_chat_file(old_filename, new_filename):
                app.notify(f"Renamed chat '{old_filename}' to '{new_filename}'.", severity="success")
                app.run_worker(populate_chat_list(app))
                # Update current_chat_file if it was the renamed one
                if app.current_chat_file and app.current_chat_file.endswith(old_filename):
                    app.current_chat_file = os.path.join("chats", new_filename)
            else:
                app.notify(f"Failed to rename chat '{old_filename}' to '{new_filename}'. Name already exists or file not found.", severity="error")

    app.push_screen(InputScreen(f"New name for '{old_filename}':", placeholder=old_filename), callback=handle_rename)


async def on_input_submitted(app, event):
    """Handle user input submission."""

    # strip() removes leading and trailing whitespace, including newlines
    user_message = event.value.strip()
    if user_message == "":
        return

    event.input.clear()
    app.messages.append({"role": "user", "content": user_message})
    
    output_log = app.query_one("#message-log", RichLog)
    output_log.write(f"[bold cyan]You:[/bold cyan] {wrap_for_long(user_message)}\n")

    if app.current_chat_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        app.current_chat_file = os.path.join("chats", f"chat_{timestamp}.json")

    # API call
    try:
        response = await call_api(app.messages, app.config)
        ai_message = response["choices"][0]["message"]["content"]
        
        app.messages.append({"role": "assistant", "content": ai_message})
        output_log.write(f"[bold green]AI:[/bold green] {wrap_for_long(ai_message)}\n")
        save_chat(app.messages, app.current_chat_file)
        app.run_worker(populate_chat_list(app))
        output_log.scroll_end()
        update_model_indicator(app)

    except Exception as e:
        # If the last message was from the user, remove it to avoid sending it again on retry
        if app.messages and app.messages[-1]["role"] == "user":
            app.messages.pop()

        output_log.write(f"[bold red]Errore:[/bold red] {wrap_for_long(str(e))}\n")
        app.notify(f"Errore API: {e}", severity="error")