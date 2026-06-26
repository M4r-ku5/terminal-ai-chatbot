import os
from rich.console import Console
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.styles import Style
from datetime import datetime
from config import load_config, save_config


# Initialize Rich console for styled terminal output
console = Console()

def run_menu(options):
    """Run interactive menu loop using prompt_toolkit."""

    if options is None:
        options = ["New chat", "Load chat", "Settings", "Quit"]

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

    # Application: the main TUI Loop. app.run() blocks until exit() is called
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


def render_menu(options, selected):
    """Render the interactive menu."""
    for i, option in enumerate(options):
        if i == selected:
            console.print(f" [bold cyan]-> {option}[/bold cyan]")
        else:
            console.print(f" {option}")


def list_chat_files():
    """Return a sorted list of .json filenames in the chats directory."""
    if not os.path.isdir("chats"):
        return []
    files = [f for f in os.listdir("chats") if f.endswith(".json")]
    return sorted(files, reverse=True)


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


def settings_menu(config):
    """Show the settings submenu."""
    
    while True:
        options = ["..",
                   f"Model: {config['model']}",
                   f"History length: {config['history_length']}",
                   f"Auto-compact: {'Yes' if config['auto_compact'] is True else 'No'}",
                   ]
        selected_index = run_menu(options)
        if selected_index is None:
            break

        # Back
        if selected_index == 0:
            break

        # Change model
        elif selected_index == 1:
            new_model = input("Model ID: ").strip()
            if new_model:
                config["model"] = new_model
                save_config(config)

        # Change history length
        elif selected_index == 2:
            while True:
                try:
                    new_history_length = input("New history length (0-50): ").strip()
                    if new_history_length == "":
                        break
                    v = int(new_history_length)
                    if 0 <= v <= 50:
                        config["history_length"] = v
                        save_config(config)
                        break
                    else:
                        print("You must insert a value between 0 and 50.")
                except ValueError:
                    print("Please insert an integer number.")
        
        # Toggle auto-compact
        elif selected_index == 3:
            config["auto_compact"] = not config["auto_compact"]
            save_config(config)
        
    return config