from textual.screen import ModalScreen
from textual.widgets import Input, Switch, Button, Label
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult



class SettingsScreen(ModalScreen):
    """Modal screen for settings configuration."""


    def __init__(self, config: dict) -> None:
        """Initialize the settings screen with the provided configuration."""

        super().__init__()
        # Save the config into the current instance
        self.config = config
    

    def compose(self) -> ComposeResult:
        """Build the settings form UI."""

        yield Vertical(
            Label("Settings", id="settings-title"),
            Label("Model"),
            Input(
                value=self.config.get("model", ""),
                id="model-input",
                placeholder="e.g. nvidia/nemotron-3-nano-30b-a3b:free"
            ),
            Label("History Length (0 = unlimited)"),
            Input(
                value=str(self.config.get("history_length", 20)),
                id="history-input",
                type="integer",
            ),
            Label("Auto-compact:"),
            Switch(
                value=self.config.get("auto_compact", False),
                id="autocompact-switch"
            ),
            Horizontal(
                Button("Save", variant="primary", id="save-button"),
                Button("Cancel", variant="default", id="cancel-button")
            ),
            id="settings-container"
        )


    def on_mount(self) -> None:
        """Focus the first input field when the settings screen is mounted."""
        self.query_one("#model-input", Input).focus()
    

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Save and Cancel button presses."""

        if event.button.id == "save-button":
            # Reads the values from the input fields
            model = self.query_one("#model-input", Input).value.strip()
            history = self.query_one("#history-input", Input).value.strip()
            autocompact = self.query_one("#autocompact-switch", Switch).value

            # Validate model input
            if not model:
                self.notify("Model cannot be empty.", severity="error")
                return

            # Validate history length input
            try:
                # Default to 20 if the input is empty
                history_length = int(history) if history else 20
                if history_length < 0 or history_length > 50:
                    raise ValueError
            except ValueError:
                self.notify("History length must be 0-50.", severity="error")
                return
            
            # Update the config dictionary and return it to the main app
            new_config = {
                "model": model,
                "history_length": history_length,
                "auto_compact": autocompact
            }
            # Dismiss the settings screen and return the new configuration
            self.dismiss(new_config)

        else:
            # Dismiss the settings screen without saving changes
            self.dismiss(None)