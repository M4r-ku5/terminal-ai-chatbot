# Terminal AI Chatbot

A terminal-based chatbot that uses the OpenRouter API to interact with AI language models directly from the command line.

## Prerequisites

- Python 3.7+
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
   pip install requests
   ```

3. Set your OpenRouter API key as an environment variable:

   **PowerShell:**
   ```powershell
   $env:OPENROUTER_API_KEY="your_api_key_here"
   ```

   **CMD:**
   ```cmd
   set OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
```bash
python main.py
```

You will be prompted to enter a message. The AI will respond and the program will exit.

## Model

By default, the chatbot uses `arcee-ai/trinity-large-thinking:free` (a free model available on OpenRouter). You can change the model in `main.py` by editing the `"model"` field in the request body.