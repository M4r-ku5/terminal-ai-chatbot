from textual.app import App, ComposeResult
from .layout import CSS, BINDINGS, compose
from .actions import (
    on_mount,
    populate_chat_list,
    action_load_chat,
    action_new_chat,
    action_settings,
    on_input_submitted,
)
from .tokens import update_model_indicator, estimate_chat_tokens
from .api import call_api, fetch_and_update_model_info


class ChatApp(App):
    CSS = CSS
    BINDINGS = BINDINGS

    def compose(self) -> ComposeResult:
        return compose(self)

    # wiring: this is a workaround to make the functions from actions.py available in the app instance
    on_mount = on_mount
    populate_chat_list = populate_chat_list
    action_load_chat = action_load_chat
    action_new_chat = action_new_chat
    action_settings = action_settings
    on_input_submitted = on_input_submitted
    update_model_indicator = update_model_indicator
    estimate_chat_tokens = estimate_chat_tokens
    call_api = call_api
    fetch_and_update_model_info = fetch_and_update_model_info


if __name__ == "__main__":
    ChatApp().run()
