from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, RichLog, Input, Static
from textual.binding import Binding


CSS = """
    #sidebar {
        width: 40;
        border: solid $primary;
    }
    #chat-area {
        width: 1fr;
        border: solid $secondary;
    }
    #message-log {
        height: 1fr;
        width: 100%;
        text-wrap: wrap;
    }
    #input-bar {
        height: 3;
        dock: bottom;
    }
    #settings-container {
        width: 60;
        height:auto;
        border: solid $primary;
        padding: 1 2;
    }
    #settings-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #settings-container Label {
        margin-top: 1;
    }
    #settings-container Input {
        width: 100%;
    }
    #settings-container Switch {
        margin-top: 1;
    }
    #settings-container Horizontal {
        margin-top: 2;
        width: 100%;
        align-horizontal: right;
    }
    #bottom-bar {
        dock: bottom;
        height: 4;
    }
    #model-indicator {
        width: 1fr;
        height: 1;
        content-align-vertical: middle;
        padding: 0 1;
        text-style: bold;
    }
    #input-bar {
        width: 1fr;
        height: 3;
    }
    #confirm-dialog, #input-dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        border: solid $primary;
        background: $surface;
        align: center middle;
    }
    #confirm-message, #input-prompt {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    #confirm-buttons, #input-buttons {
        width: 100%;
        align-horizontal: center;
        margin-top: 1;
    }
    #confirm-buttons Button, #input-buttons Button {
        min-width: 10;
        margin: 0 1;
    }
"""

BINDINGS = [
    Binding("enter", "load_chat", "Load Chat"),
    Binding("ctrl+l", "load_chat", "Load Chat"),
    Binding("ctrl+n", "new_chat", "New Chat"),
    Binding("ctrl+q", "quit", "Quit"),
    Binding("ctrl+s", "settings", "Settings"),
    Binding("ctrl+d", "delete_chat", "Delete Chat"),
    Binding("ctrl+r", "rename_chat", "Rename Chat")
]


def compose(app) -> ComposeResult:
    """Compose the UI layout. Divide the screen into a sidebar for chat selection
    and a main area for chat messages."""

    # show_clock=True adds a clock to the header
    yield Header(show_clock=True)

    with Horizontal():
        with Vertical(id="sidebar"):
            yield ListView(id="chat-list")

        with Vertical(id="chat-area"):
            # markup=True allows for rich text formatting in the log
            yield RichLog(id="message-log", markup=True)
            with Vertical(id="bottom-bar"):
                yield Input(placeholder="Write a message...", id="input-bar")
                yield Static("", id="model-indicator")

    yield Footer()