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

def test_run_task():
    with patch("src.explorer.SeleniumDriver") as mock_driver_cls, \
         patch("src.explorer.ActionEngine") as mock_action_engine_cls, \
         patch("src.explorer.WorldModel") as mock_world_model_cls, \
         patch("src.explorer.WebAgent") as mock_agent_cls, \
         patch("src.explorer.GeminiContext") as mock_context_cls:
        
        # Setup mocks
        mock_context = MagicMock()
        mock_context_cls.return_value = mock_context

        mock_driver = MagicMock()
        mock_driver_cls.return_value = mock_driver
        
        mock_action_engine = MagicMock()
        mock_action_engine_cls.from_context.return_value = mock_action_engine
        
        mock_world_model = MagicMock()
        mock_world_model_cls.from_context.return_value = mock_world_model
        
        mock_agent = MagicMock()
        mock_agent_cls.return_value = mock_agent
        mock_agent.logger.logs = [{"step": 1, "action": "click"}]
        
        # Execute
        explorer = Explorer()
        history = explorer.run_task("https://example.com", "Click the button")
        
        # Assertions
        mock_driver_cls.assert_called_once_with(headless=True)
        mock_action_engine_cls.from_context.assert_called_once()
        mock_world_model_cls.from_context.assert_called_once()
        mock_agent_cls.assert_called_once_with(mock_world_model, mock_action_engine)
        
        mock_agent.get.assert_called_once_with("https://example.com")
        mock_agent.run.assert_called_once_with("Click the button")
        mock_driver.driver.quit.assert_called_once()
        
        assert history == [{"step": 1, "action": "click"}]
