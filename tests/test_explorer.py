import pytest
from unittest.mock import MagicMock, patch
from src.explorer import Explorer

def test_explorer_initialization():
    with patch("src.explorer.GeminiContext") as mock_context:
        mock_instance = MagicMock()
        mock_context.return_value = mock_instance
        
        explorer = Explorer(model_name="models/gemini-1.5-flash")
        
        assert explorer.context == mock_instance
        mock_context.assert_called_once_with(llm="models/gemini-1.5-flash")
