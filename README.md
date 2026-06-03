# Terminal AI Chatbot

A terminal-based chatbot that uses the OpenRouter API to interact with AI language models directly from the command line.

## Prerequisites

- Python 3.7+
- pip (comes with Python)
- An OpenRouter API key (get one at https://openrouter.ai/keys)
- python-dotenv (installed via pip)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/M4r-ku5/terminal-ai-chatbot.git
   cd terminal-ai-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install requests python-dotenv
   ```

3. Create a `.env` file in the project root and add your API key:
   ```bash
   OPENROUTER_API_KEY=your_api_key_here
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
Type your message and press Enter to get a response from the AI. Type `/exit` to quit. The AI retains context from previous message in the conversation.

## Model

By default, the chatbot uses `arcee-ai/trinity-mini` (a free model available on OpenRouter). You can change the model in `main.py` by editing the `"model"` field in the request body.