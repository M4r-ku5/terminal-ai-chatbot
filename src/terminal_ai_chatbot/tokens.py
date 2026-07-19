from textual.widgets import Static



def estimate_tokens(text: str | int) -> int:
    """Estimate the number of tokens in a given text."""

    # if the input is an integer, we assume it's a character count and estimate tokens accordingly
    if isinstance(text, int):
        return max(1, text // 4)
    
    # if the input is a string, we estimate tokens based on character count
    else:
        return max(1, len(text) // 4)
    

def update_model_indicator(self, max_tokens: int | None = None) -> None:
        """Update the model indicator in the UI with current token usage and max tokens."""
        
        if max_tokens is None:
            max_tokens = getattr(self, "_max_tokens", None)

        tokens = self.estimate_chat_tokens()
        model = self.config.get("model", "unknown")
        if max_tokens:
            pct = (tokens / max_tokens) * 100

            # ":," formats the number with commas as thousands separators
            text = f"Model: {model} | Tokens: ~{tokens:,} / {max_tokens:,} ({pct:.0f}%)"
        else:
            text = f"Model: {model} | Tokens: ~{tokens:,}"

        self.query_one("#model-indicator", Static).update(text)


def estimate_chat_tokens(self) -> int:
    """Estimate total tokens in the current chat."""
    
    total_chars = sum(len(m.get("content", "")) for m in self.messages)
    return estimate_tokens(total_chars)