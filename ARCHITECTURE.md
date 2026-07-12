# Architecture Document

## Overview
Terminal AI Chatbot - A split-pane Textual TUI application for chatting with AI models via OpenRouter API.

---

## Current Workflow

### 1. Application Startup (`on_mount`)
```
┌─────────────────────────────────────────────────────────────┐
│ ChatApp.on_mount()                                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Create chats/ directory if not exists                    │
│ 2. Load config from config.json (model, history_length,     │
│    auto_compact)                                            │
│ 3. Initialize state:                                        │
│    - self.current_chat_file = None                          │
│    - self.messages = []                                     │
│ 4. Populate chat list sidebar (populate_chat_list)          │
│ 5. Set window title                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2. Chat List Population (`populate_chat_list`)
```
┌─────────────────────────────────────────────────────────────┐
│ ChatApp.populate_chat_list()                                │
├─────────────────────────────────────────────────────────────┤
│ 1. Query ListView#chat-list                                 │
│ 2. Clear existing items                                     │
│ 3. For each file from chat_logic.list_chat_files():         │
│    - Create safe_id (filename without .json)                │
│    - Create ListItem with Label(filename), id=safe_id       │
│    - Store original filename as item.filename               │
│    - Append to ListView                                     │
└─────────────────────────────────────────────────────────────┘
```

### 3. Loading a Chat (`action_load_chat`)
```
┌─────────────────────────────────────────────────────────────┐
│ User presses Enter/Ctrl+L on highlighted chat               │
├─────────────────────────────────────────────────────────────┤
│ 1. Get highlighted ListItem from ListView                   │
│ 2. Reconstruct filename: safe_id + ".json"                  │
│ 3. Build filepath: chats/{filename}                         │
│ 4. Call chat_logic.load_chat_messages(filepath)             │
│ 5. If successful:                                           │
│    a. Update internal state:                                │
│       - self.messages = messages[:] (copy)                  │
│       - self.current_chat_file = filepath                   │
│    b. Clear RichLog#message-log                             │
│    c. Apply history_length filter from config               │
│    d. Render each message with markup:                      │
│       - User: [bold cyan]You:[/bold cyan] {content}         │
│       - AI:   [bold green]AI:[/bold green] {content}        │
└─────────────────────────────────────────────────────────────┘
```

### 4. Starting New Chat (`action_new_chat`)
```
┌─────────────────────────────────────────────────────────────┐
│ User presses Ctrl+N                                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Clear RichLog#message-log                                │
│ 2. Reset state:                                             │
│    - self.current_chat_file = None                          │
│    - self.messages = []                                     │
│ 3. Show notification                                        │
└─────────────────────────────────────────────────────────────┘
```

### 5. Sending a Message (`on_input_submitted`)
```
┌─────────────────────────────────────────────────────────────┐
│ User types in Input#input-bar and presses Enter             │
├─────────────────────────────────────────────────────────────┤
│ 1. Get user_message = event.value.strip()                   │
│ 2. If empty, return                                         │
│ 3. Clear input field                                        │
│ 4. Append to self.messages: {"role": "user", "content": ...}│
│ 5. Write to RichLog: [bold cyan]You:[/bold cyan] {msg}      │
│ 6. If self.current_chat_file is None:                       │
│    - Generate timestamp filename                            │
│    - Set self.current_chat_file                             │
│ 7. Call await self.call_api(self.messages, self.config)     │
│ 8. On success:                                              │
│    a. Extract ai_message from response                      │
│    b. Append to self.messages: {"role": "assistant", ...}   │
│    c. Write to RichLog: [bold green]AI:[/bold green] {msg}  │
│    d. Call save_chat(self.messages, self.current_chat_file) │
│    e. Scroll RichLog to end                                 │
│ 9. On error:                                                │
│    a. Remove last user message from self.messages           │
│    b. Write error to RichLog                                │
│    c. Show notification                                     │
└─────────────────────────────────────────────────────────────┘
```

### 6. API Call (`call_api`)
```
┌─────────────────────────────────────────────────────────────┐
│ async def call_api(messages, config)                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Get event loop                                           │
│ 2. Define _sync_call() using requests.post:                 │
│    - URL: https://openrouter.ai/api/v1/chat/completions     │
│    - Headers: Authorization Bearer, Content-Type JSON       │
│    - Body: model, messages                                  │
│    - Timeout: 30s                                           │
│ 3. Run in executor: await loop.run_in_executor(None, _sync) │
│ 4. Check status_code != 200 → raise Exception               │
│ 5. Return response.json()                                   │
└─────────────────────────────────────────────────────────────┘
```

### 7. Chat Persistence (`chat_logic.py`)
```
┌─────────────────────────────────────────────────────────────┐
│ save_chat(messages, filepath)                               │
├─────────────────────────────────────────────────────────────┤
│ - Write messages list as JSON with indent=2, ensure_ascii  │
│   False                                                     │
│ - Catch exceptions, print error                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ load_chat_messages(filepath)                                │
├─────────────────────────────────────────────────────────────┤
│ - Read JSON file, return list                               │
│ - Catch FileNotFoundError, JSONDecodeError → return None    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ list_chat_files()                                           │
├─────────────────────────────────────────────────────────────┤
│ - List chats/ directory for .json files                     │
│ - Return sorted descending (newest first)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## UI Layout (Textual)

```
┌─────────────────────────────────────────────────────────────┐
│ Header (title + clock)                                      │
├──────────────────────┬──────────────────────────────────────┤
│ Sidebar (40 cols)    │ Chat Area (1fr)                      │
│ ┌────────────────┐   │ ┌──────────────────────────────────┐ │
│ │ ListView       │   │ │ RichLog#message-log              │ │
│ │ #chat-list     │   │ │ - markup=True                    │ │
│ │ - chat_1.json  │   │ │ - text-wrap: wrap                │ │
│ │ - chat_2.json  │   │ │ - height: 1fr                    │ │
│ │ - chat_3.json  │   │ ├──────────────────────────────────┤ │
│ │                │   │ │ Input#input-bar                  │ │
│ │                │   │ │ - placeholder: "Write..."        │ │
│ │                │   │ │ - height: 3, dock: bottom        │ │
│ └────────────────┘   │ └──────────────────────────────────┘ │
├──────────────────────┴──────────────────────────────────────┤
│ Footer (keybindings)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Keybindings

| Key | Action | Handler |
|-----|--------|---------|
| `↑` / `↓` | Navigate chat list | Built-in ListView |
| `Enter` | Load selected chat | `action_load_chat` |
| `Ctrl+L` | Load selected chat | `action_load_chat` |
| `Ctrl+N` | New chat | `action_new_chat` |
| `Ctrl+Q` | Quit | Built-in `action_quit` |
| `Tab` | Switch focus | Built-in |
| `Enter` (in input) | Send message | `on_input_submitted` |

---

## State Management

| Attribute | Purpose | Updated By |
|-----------|---------|------------|
| `self.config` | User settings (model, history_length, auto_compact) | `on_mount` |
| `self.current_chat_file` | Path to currently loaded chat file | `action_load_chat`, `on_input_submitted`, `action_new_chat` |
| `self.messages` | In-memory message history for current chat | `action_load_chat`, `on_input_submitted`, `action_new_chat` |

---

## Configuration (`config.json`)

```json
{
  "model": "nvidia/nemotron-3-nano-30b-a3b:free",
  "history_length": 20,
  "auto_compact": false
}
```

- `model`: OpenRouter model ID
- `history_length`: Number of previous messages to send (0 = all)
- `auto_compact`: Planned feature for summarization

---

## Project Structure

```
terminal-ai-chatbot/
├── app.py              # Main Textual application (ChatApp)
├── chat_logic.py       # Persistence & API helpers
├── config.py           # Config load/save
├── config.json         # User settings
├── main.py             # Legacy entry point (deprecated)
├── .env                # OPENROUTER_API_KEY
├── chats/              # Saved conversations (JSON)
├── README.md           # User documentation
└── ARCHITECTURE.md     # This file
```

---

## Todo List

### ✅ Implemented

- [x] **Textual split-pane UI** - Sidebar + chat area with Header/Footer
- [x] **Chat list population** - Loads `.json` files from `chats/` on startup
- [x] **Chat loading** - Enter/Ctrl+L loads selected chat, shows messages with markup
- [x] **New chat** - Ctrl+N clears state and UI
- [x] **Message sending** - Input field with Enter to send
- [x] **API integration** - Async call to OpenRouter via `run_in_executor`
- [x] **Auto-save** - Every user+AI message pair saved immediately
- [x] **Chat switching** - State preserved when loading different chats
- [x] **History length filtering** - Respects `config.history_length`
- [x] **Text wrapping** - Long messages wrap in RichLog
- [x] **Error handling** - API errors shown in chat, user message rolled back
- [x] **README.md** - Updated for Textual UI
- [x] **Config system** - JSON-based with `config.py` loader

### 🔄 In Progress / Partially Implemented

- [ ] **Settings modal** - `action_settings` exists but is placeholder (`...`)
- [ ] **Model indicator in UI** - Show current model in header/footer

### 📋 Planned (Not Started)

- [ ] **Delete/archive chats** - Remove or archive old conversations
- [ ] **Auto-compact/summarization** - Summarize old messages when token limit approached
- [ ] **Message formatting** - Code blocks, markdown rendering in RichLog
- [ ] **Streaming responses** - Show AI response token-by-token
- [ ] **Keyboard shortcuts help** - Overlay with all keybindings
- [ ] **Chat search/filter** - Filter chat list by name/date
- [ ] **Export chat** - Save as markdown/text
- [ ] **Theme support** - Light/dark mode toggle
- [ ] **Multi-model support** - Switch models per chat
- [ ] **Token usage display** - Show tokens used in current chat

---

## Known Issues / Technical Debt

1. **Imports cleanup** - `app.py` has unused imports (`from fileinput import filename`, `from pyexpat.errors import messages`)
2. **Legacy `chat()` function** - `chat_logic.py` still contains old prompt_toolkit `chat()` function (unused)
3. **No input validation** - Empty API key handling exits process.exit(1) in chat_logic on import
4. **Blocking exit** - `exit(1)` in chat_logic on missing API key kills entire process
5. **No tests** - No unit/integration tests
6. **Hardcoded timeout** - 30s API timeout not configurable

---

## Data Flow Summary

```
User Input → on_input_submitted → self.messages.append(user)
                    ↓
            call_api(self.messages) → OpenRouter API
                    ↓
            response.json() → extract ai_message
                    ↓
            self.messages.append(assistant) → save_chat()
                    ↓
            RichLog.write() → UI update → scroll_end()
```

---

## Future Architecture Considerations

1. **Separate API layer** - Move HTTP logic to dedicated module
2. **Event-driven updates** - Use Textual's message system for UI updates
3. **Background workers** - Use `run_worker` for API calls instead of `run_in_executor`
4. **Settings screen** - Implement as `ModalScreen` with form inputs
5. **Plugin system** - Allow custom formatters/renderers for messages