import os
import datetime
import asyncio
import requests
from config import load_config
from chat_logic import list_chat_files, load_chat_messages, save_chat
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, RichLog, Input, ListItem, Label
from textual.binding import Binding



class ChatApp(App):
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
        text-wrap: wrap
    }
    #input-bar {
        height: 3;
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding("enter", "load_chat", "Load Chat"),
        Binding("ctrl+l", "load_chat", "Load Chat"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+q", "quit", "Quit")
    ]
    


    def compose(self) -> ComposeResult:
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
                yield Input(placeholder="Write a message...", id="input-bar")

        yield Footer()
    

    def on_mount(self) -> None:
        """Initialize the app state when the app is mounted."""
        
        os.makedirs("chats", exist_ok=True)
        self.config = load_config()
        self.current_chat_file = None
        self.messages = []
        self.populate_chat_list()
        self.title = "Terminal AI Chatbot"
    

    def populate_chat_list(self):
        """Populate the chat list in the sidebar with available chat files."""

        chat_list = self.query_one("#chat-list", ListView)
        chat_list.clear()

        for filename in list_chat_files():
            safe_id = filename.replace(".json", "")
            item = ListItem(Label(filename), id=safe_id)
            item.filename = filename
            chat_list.append(item)
    

    def action_load_chat(self):
        """Load the selected chat from the list and display it in the message log."""

        chat_list = self.query_one("#chat-list", ListView)

        if chat_list.highlighted_child:
            safe_id = chat_list.highlighted_child.id
            filename = safe_id + ".json"
            filepath = os.path.join("chats", filename)
            messages = load_chat_messages(filepath)

            if messages:
                message_log = self.query_one("#message-log", RichLog)
                message_log.clear()

                self.messages = messages[:]
                self.current_chat_file = filepath

                # Default value for history_length is 20 if not specified in config
                history_len = self.config.get("history_length", 20)
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
                self.notify("Loading error.", severity="error")


    def action_settings(self): ...


    def action_new_chat(self): 
        """Clears the current chat and starts a new one."""

        message_log = self.query_one("#message-log", RichLog)
        message_log.clear()
        self.current_chat_file = None
        self.messages = []
        self.notify("New chat started. Type your message to begin.")


    async def on_input_submitted(self, event):
        """Handle user input submission."""

        # strip() removes leading and trailing whitespace, including newlines
        user_message = event.value.strip()
        if user_message == "":
            return

        event.input.clear()
        self.messages.append({"role": "user", "content": user_message})
        
        output_log = self.query_one("#message-log", RichLog)
        output_log.write(f"[bold cyan]You:[/bold cyan] {user_message}\n")

        if self.current_chat_file is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.current_chat_file = os.path.join("chats", f"chat_{timestamp}.json")

        # API call
        try:
            response = await self.call_api(self.messages, self.config)
            ai_message = response["choices"][0]["message"]["content"]
            
            self.messages.append({"role": "assistant", "content": ai_message})
            output_log.write(f"[bold green]AI:[/bold green] {ai_message}\n")
            save_chat(self.messages, self.current_chat_file)
            output_log.scroll_end()

        except Exception as e:
            # If the last message was from the user, remove it to avoid sending it again on retry
            if self.messages and self.messages[-1]["role"] == "user":
                self.messages.pop()

            output_log.write(f"[bold red]Errore:[/bold red] {e}\n")
            self.notify(f"Errore API: {e}", severity="error")


    async def call_api(self, messages, config):
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



if __name__ == "__main__":
    app = ChatApp()
    app.run()
