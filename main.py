import os
import requests
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.styles import Style
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Rich console for styled terminal output
console = Console()


API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found.")
    exit(1)


def render_menu(options, selected):
    """Render the interactive menu."""
    for i, option in enumerate(options):
        if i == selected:
            console.print(f" [bold cyan]-> {option}[/bold cyan]")
        else:
            console.print(f" {option}")


def chat(initial_messages=None, filename=None):
    """Chat loop, handles chat save in local memory and AI request/response."""

    messages = [] if initial_messages is None else list(initial_messages)

    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"chats/chat_{timestamp}.json"

    if messages:
        last_messages = messages[-20:]
        for m in last_messages:
            if m["role"] == "user":
                 print("You:", end=" ")
            else:
                print("AI:", end=" ")
            print(m["content"].lstrip('\n'))


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
                "model": "arcee-ai/trinity-mini",
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


def list_chat_files():
    """Return a sorted list of .json filenames in the chats directory."""
    if not os.path.isdir("chats"):
        return []
    files = [f for f in os.listdir("chats") if f.endswith(".json")]
    return sorted(files, reverse=True)


def load_chat_messages(filepath):
    """Load messages from a JSON file. Return list of messages, or None on error."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"\n[ERROR] Could not load chat '{filepath}': {e}")
        return None
    

def select_chat_file():
    """Show a menu of available chat files and return the selected filename, or None."""
    files = list_chat_files()
    if not files:
        print("\n[Info] No chats found in 'chats/' folder.")
        input("Press Enter to return to menu...")
        return None

    selected_index = run_menu(files)
    if selected_index is None:
        return None
    return files[selected_index]


def run_menu(options):
    """Run interactive menu loop using prompt_toolkit."""

    if options is None:
        options = ["New chat", "Load chat", "Settings", "Exit"]
    
    selected = 0

    # Create a registry that maps keys to handler functions
    kb = KeyBindings()

    # Arrow up: move selection up, clamped at 0
    @kb.add(Keys.Up)
    def go_up(event):
        nonlocal selected
        selected = max(0, selected - 1)

    # Arrow down: move selection down, clamped at last index
    @kb.add(Keys.Down)
    def go_down(event):
        nonlocal selected
        selected = min(len(options) - 1, selected + 1)

    # Enter: confirm selection and exit the app with the chosen index
    @kb.add(Keys.Enter)
    def select(event):
        event.app.exit(result=selected)
    
    # 'q' or Ctrl+c: quit without selecting
    @kb.add("q")
    @kb.add("c-c")
    def quit(event):
        event.app.exit(result=None)
    
    # Build the menu text as a list of (style, text) tuples.
    # Called every time the screen needs to be redrawn
    def get_menu_text():
        lines = []
        for i, option in enumerate(options):
            if i == selected:
                lines.append(("class:selected", f"-> {option}\n"))
            else:
                lines.append(("class:unselected", f" {option}\n"))
        return lines
    
    control = FormattedTextControl(get_menu_text)
    window = Window(control, always_hide_cursor=True)
    layout = Layout(window)

    # CSS-like style definitions for "selected" and "unselected" classes
    style = Style.from_dict({
        "selected": "reverse bold cyan",
        "unselected": "white",
    })

    # Application: the main TUI Loop. app.run() blocks until exit() is called.
    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        mouse_support=False,
        style=style,
    )

    # app.run() returns the value passed to event.app.exit(result=...)
    result = app.run()
    return result


# Script entry point
if __name__ == "__main__":

    # Create "chats" folder if not exists
    os.makedirs("chats", exist_ok=True)

    while True:
        # Show the menu and run the selected action
        result = run_menu(["New chat", "Load chat", "Settings", "Exit"])

        # Index 0 = "New chat": start an interactive chat session
        if result == 0:
            chat()

        # Index 1 = "Load chat": opens saved chats menu
        elif result == 1:
            selected_file = select_chat_file()
            if selected_file is not None:
                filepath = os.path.join("chats", selected_file)
                initial_messages = load_chat_messages(filepath)
                chat(initial_messages=initial_messages, filename=filepath)

        # Exit
        elif result == 3:
            break

        # User pressed q or Ctrl+c
        elif result is None:
            break