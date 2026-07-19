import pytest
from src.terminal_ai_chatbot.tokens import estimate_tokens


class TestEstimateTokens:
    """Tests for the estimate_tokens function."""

    def test_estimate_tokens_string(self):
        """Test token estimation from string."""
        text = "Hello world"
        tokens = estimate_tokens(text)
        assert tokens == max(1, len(text) // 4)

    def test_estimate_tokens_int(self):
        """Test token estimation from int (char count)."""
        chars = 100
        tokens = estimate_tokens(chars)
        assert tokens == max(1, chars // 4)

    def test_estimate_tokens_empty_string(self):
        """Test minimum token count for empty string."""
        tokens = estimate_tokens("")
        assert tokens == 1

    def test_estimate_tokens_single_char(self):
        """Test minimum token count for single char."""
        tokens = estimate_tokens("a")
        assert tokens == 1

    def test_estimate_tokens_zero_int(self):
        """Test minimum token count for zero int."""
        tokens = estimate_tokens(0)
        assert tokens == 1

    def test_estimate_tokens_long_text(self):
        """Test token estimation for longer text."""
        text = "a" * 1000
        tokens = estimate_tokens(text)
        assert tokens == 1000 // 4

    def test_estimate_tokens_unicode(self):
        """Test token estimation with unicode characters."""
        text = "Ciao mondo! 🌍"
        tokens = estimate_tokens(text)
        assert tokens == max(1, len(text) // 4)


class TestUpdateModelIndicator:
    """Tests for update_model_indicator method (requires mocking)."""

    def test_update_model_indicator_no_max_tokens(self, mocker):
        """Test update_model_indicator without max_tokens."""
        from textual.widgets import Static
        
        # Create mock app instance
        mock_app = mocker.MagicMock()
        mock_app.config = {"model": "test/model"}
        mock_app.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        mock_app._max_tokens = None
        # Mock estimate_chat_tokens to return an integer
        mock_app.estimate_chat_tokens.return_value = 10
        
        # Mock query_one to return a mock Static widget
        mock_static = mocker.MagicMock(spec=Static)
        mock_app.query_one.return_value = mock_static
        
        # Call the method
        from src.terminal_ai_chatbot.tokens import update_model_indicator
        update_model_indicator(mock_app)
        
        # Verify query_one was called with correct selector
        mock_app.query_one.assert_called_once_with("#model-indicator", Static)
        
        # Verify static update was called
        mock_static.update.assert_called_once()
        call_args = mock_static.update.call_args[0][0]
        assert "Model: test/model" in call_args
        assert "Tokens:" in call_args

    def test_update_model_indicator_with_max_tokens(self, mocker):
        """Test update_model_indicator with max_tokens."""
        from textual.widgets import Static
        
        mock_app = mocker.MagicMock()
        mock_app.config = {"model": "test/model"}
        mock_app.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        mock_app._max_tokens = 4096
        # Mock estimate_chat_tokens to return an integer
        mock_app.estimate_chat_tokens.return_value = 100
        
        mock_static = mocker.MagicMock(spec=Static)
        mock_app.query_one.return_value = mock_static
        
        from src.terminal_ai_chatbot.tokens import update_model_indicator
        update_model_indicator(mock_app)
        
        mock_static.update.assert_called_once()
        call_args = mock_static.update.call_args[0][0]
        assert "Model: test/model" in call_args
        assert "Tokens:" in call_args
        assert "4,096" in call_args  # Formatted with comma
        assert "%" in call_args


class TestEstimateChatTokens:
    """Tests for estimate_chat_tokens method."""

    def test_estimate_chat_tokens(self, mocker):
        """Test estimate_chat_tokens calculates correctly."""
        mock_app = mocker.MagicMock()
        mock_app.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there! How can I help?"}
        ]
        
        from src.terminal_ai_chatbot.tokens import estimate_chat_tokens
        tokens = estimate_chat_tokens(mock_app)
        
        total_chars = len("Hello") + len("Hi there! How can I help?")
        expected = max(1, total_chars // 4)
        assert tokens == expected

    def test_estimate_chat_tokens_empty(self, mocker):
        """Test estimate_chat_tokens with empty messages."""
        mock_app = mocker.MagicMock()
        mock_app.messages = []
        
        from src.terminal_ai_chatbot.tokens import estimate_chat_tokens
        tokens = estimate_chat_tokens(mock_app)
        
        assert tokens == 1  # minimum

    def test_estimate_chat_tokens_missing_content(self, mocker):
        """Test estimate_chat_tokens handles missing content key."""
        mock_app = mocker.MagicMock()
        mock_app.messages = [
            {"role": "user"},  # no content key
            {"role": "assistant", "content": "Hi"}
        ]
        
        from src.terminal_ai_chatbot.tokens import estimate_chat_tokens
        tokens = estimate_chat_tokens(mock_app)
        
        total_chars = len("") + len("Hi")
        expected = max(1, total_chars // 4)
        assert tokens == expected