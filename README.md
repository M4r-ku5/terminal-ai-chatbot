# Terminal AI Chatbot

A terminal-based AI chatbot with a split-pane Textual interface, using the OpenRouter API to interact with language models directly from the command line.

## Prerequisites

- Python 3.8+
- pip (comes with Python)
- An OpenRouter API key (get one at https://openrouter.ai/keys)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/M4r-ku5/terminal-ai-chatbot.git
   cd terminal-ai-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install requests python-dotenv rich textual
   ```

3. Create a `.env` file in the project root and add your API key:
   ```bash
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
```bash
python -m terminal_ai_chatbot
```

A split-pane interface will open:
- **Left sidebar**: List of saved chats (navigate with ↑/↓)
- **Right pane**: Chat messages area + input bar at bottom
- **Bottom bar**: Model name + token usage (used / max + percentage)

### Keybindings

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate chat list in sidebar |
| `Ctrl+L` | Load selected chat |
| `Ctrl+N` | Start new chat |
| `Ctrl+S` | Open settings |
| `Ctrl+Q` | Quit application |
| `Ctrl+D` | **Delete selected chat** (with confirmation) |
| `Ctrl+R` | **Rename selected chat** |
| `Tab` | Switch focus between sidebar and input |
| Type + `Enter` | Send message (when input focused) |

### Workflow

1. **New chat**: Press `Ctrl+N` → type message → press `Enter` → AI responds → auto-saved
2. **Load chat**: Navigate sidebar with `↑`/`↓` → press `Enter` or `Ctrl+L` to load
3. **Switch chats**: Load different chats from sidebar anytime; state is preserved
4. **Settings**: Press `Ctrl+S` → select model, history length, auto-compact (not yet implemented)
5. **Quit**: Press `Ctrl+Q` anytime
6. **Manage chats**: Select a chat in sidebar → `Ctrl+D` to delete (confirms) / `Ctrl+R` to rename

## Features

- **Split-pane Textual UI**: Sidebar for chat list, main area for conversation
- **Persistent chats**: Saved as JSON files in `chats/` directory
- **Chat management**: Delete (`Ctrl+D`) and rename (`Ctrl+R`) chats from sidebar
- **Conversational context**: Full message history sent to API each turn
- **Auto-save**: Every message (user + AI) immediately persisted
- **Settings UI** (`Ctrl+S`): Model selection (searchable dropdown from OpenRouter), history length, auto-compact toggle
- **Token indicator**: Bottom bar shows model + estimated tokens used / max context window + percentage
- **Model fetching**: Auto-fetches available text models from OpenRouter API (cached 24h)
- **Configurable**: Model, history length via `config.json` (Settings UI coming soon)
- **Free model default**: Uses `nvidia/nemotron-3-nano-30b-a3b:free` via OpenRouter

## Configuration

Settings are stored in `config.json`:
```json
{
  "model": "nvidia/nemotron-3-nano-30b-a3b:free",
  "history_length": 20,
  "auto_compact": false
}
```

- `model`: Any model ID available on OpenRouter
- `history_length`: Number of previous messages to include (0 = all)
- `auto_compact`: (Planned) Summarize old messages when token limit approached

## Model

Default: `nvidia/nemotron-3-nano-30b-a3b:free` (free tier on OpenRouter). Change via `Ctrl+S` or `config.json` or future Settings screen.