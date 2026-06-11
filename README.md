# Terminal AI Chatbot

A terminal-based chatbot that uses the OpenRouter API to interact with AI language models directly from the command line.

## Prerequisites

- Python 3.7+
- pip (comes with Python)
- An OpenRouter API key (get one at https://openrouter.ai/keys)
- python-dotenv (installed via pip)
- prompt_toolkit
- rich

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/M4r-ku5/terminal-ai-chatbot.git
   cd terminal-ai-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install requests python-dotenv prompt_toolkit rich
   ```

3. Create a `.env` file in the project root and add your API key:
   ```bash
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
   ```bash
   python main.py
   ```

An interactive menu will appear. Use the __arrow keys__ to navigate, __Enter__ to confirm, and __q__ or __Ctrl+c__ to quit.

- __New chat__: starts an interactive chat session. Type `/exit` to return to the menu.
- __Load chat__: lists saved chats; select one to continue the conversation, or q/Ctrl+c to return to the menu.
- __Settings__: (not yet implemented).


## Features

- Interactive menu with arrow-key navigation
- Conversational context: the AI remembers previous messages
- Persistent chat saving and loading (JSON files in chats/)
- Environment variable configuration via `.env` file

## Model

By default, the chatbot uses `arcee-ai/trinity-mini` (a free model available on OpenRouter). You can change the model in `main.py` by editing the `"model"` field in the request body.