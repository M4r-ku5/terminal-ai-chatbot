import os
from rich.console import Console
from config import load_config
from menu import run_menu, settings_menu, select_chat_file
from chat_logic import chat
from chat_logic import load_chat_messages


# Initialize Rich console for styled terminal output
console = Console()

# Script entry point
if __name__ == "__main__":

    # Create "chats" folder if not exists
    os.makedirs("chats", exist_ok=True)
    
    config = load_config()

    while True:
        # Show the menu and run the selected action
        result = run_menu(["New chat", "Load chat", "Settings", "Exit"])

        # Index 0 = "New chat": start an interactive chat session
        if result == 0:
            chat(config=config)

        # Index 1 = "Load chat": opens saved chats menu
        elif result == 1:
            selected_file = select_chat_file()
            if selected_file is not None:
                filepath = os.path.join("chats", selected_file)
                initial_messages = load_chat_messages(filepath)
                chat(initial_messages=initial_messages, filename=filepath, config=config)

        elif result == 2:
            config = settings_menu(config)

        # Exit
        elif result == 3:
            break

        # User pressed q or Ctrl+c
        elif result is None:
            break