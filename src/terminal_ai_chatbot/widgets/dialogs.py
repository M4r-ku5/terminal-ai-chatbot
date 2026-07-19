from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual.app import ComposeResult



class ConfirmScreen(ModalScreen[bool]):
    """Modal screen for yes/no confirmation."""

    DEFAULT_CSS = """
      ConfirmScreen {
          align: center middle;
      }
      #confirm-dialog {
          width: 60;
          height: auto;
          max-height: 25%;
          padding: 1 2;
          border: solid $primary;
          background: $surface;
      }
      #confirm-message {
          width: 100%;
          text-align: center;
          margin-bottom: 1;
      }
      #confirm-buttons {
          width: 100%;
          align-horizontal: center;
          margin-top: 1;
      }
      #confirm-buttons Button {
          min-width: 10;
          margin: 0 1;
      }
      """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]
    

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message
    
    
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, id="confirm-message"),
            Horizontal(
                Button("Yes", variant="error", id="button-yes"),
                Button("No", variant="primary", id="button-no"),
                id="confirm-buttons"
            ),
            id="confirm-dialog"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_confirm(self) -> None:
        self.dismiss(True)
    
    def action_cancel(self) -> None:
        self.dismiss(False)



class InputScreen(ModalScreen[str | None]):
    """Modal screen for text input."""
    
    DEFAULT_CSS = """
      InputScreen {
          align: center middle;
      }
      #input-dialog {
          width: 60;
          height: auto;
          max-height: 35%;
          padding: 1 2;
          border: solid $primary;
          background: $surface;
      }
      #input-prompt {
          width: 100%;
          text-align: center;
          margin-bottom: 1;
      }
      #input-field {
          width: 100%;
          margin-bottom: 1;
      }
      #input-buttons {
          width: 100%;
          align-horizontal: center;
          margin-top: 1;
      }
      #input-buttons Button {
          min-width: 10;
          margin: 0 1;
      }
      """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Submit"),
    ]
    

    def __init__(self, prompt: str, placeholder: str = "") -> None:
        super().__init__()
        self.prompt = prompt
        self.placeholder = placeholder
    

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.prompt, id="input-prompt"),
            Input(placeholder=self.placeholder, id="input-field"),
            Horizontal(
                Button("OK", variant="primary", id="button-ok"),
                Button("Cancel", variant="default", id="button-cancel"),
                id="input-buttons"
            ),
            id="input-dialog"
        )
    

    def on_mount(self) -> None:
        self.query_one("#input-field", Input).focus()
    

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button-ok":
            value = self.query_one("#input-field", Input).value
            self.dismiss(value if value else None)
        else:
            self.dismiss(None)
    

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value if event.value else None)
    

    def action_submit(self) -> None:
        value = self.query_one("#input-field", Input).value
        self.dismiss(value if value else None)
    

    def action_cancel(self) -> None:
        self.dismiss(None)