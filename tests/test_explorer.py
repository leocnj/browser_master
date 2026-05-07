import pytest
from unittest.mock import MagicMock, patch
from src.explorer import Explorer

def test_explorer_initialization():
    # Patch the components Explorer initializes to avoid real API calls
    # We patch at the module level where they are imported
    with patch("src.explorer.Gemini") as mock_llm_cls, \
         patch("src.explorer.GeminiMultiModal") as mock_mm_llm_cls, \
         patch("src.explorer.GeminiContext") as mock_ctx_cls:
        
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        
        mock_mm_llm = MagicMock()
        mock_mm_llm_cls.return_value = mock_mm_llm
        
        mock_ctx = MagicMock()
        mock_ctx_cls.return_value = mock_ctx
        
        # The __init__ uses patch() internally, which makes tracking the direct call tricky
        # but we can verify the context is set.
        explorer = Explorer(model_name="models/gemini-2.5-flash")
        
        assert explorer.context == mock_ctx

def test_run_task():
    # Patch everything to avoid side effects
    with patch("src.explorer.Gemini"), \
         patch("src.explorer.GeminiMultiModal"), \
         patch("src.explorer.GeminiContext"), \
         patch("src.explorer.SeleniumDriver") as mock_driver_cls, \
         patch("src.explorer.ActionEngine") as mock_action_engine_cls, \
         patch("src.explorer.WorldModel") as mock_world_model_cls, \
         patch("src.explorer.WebAgent") as mock_agent_cls:
        
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
        mock_agent.get.assert_called_once_with("https://example.com")
        mock_driver.driver.quit.assert_called_once()
        
        assert history == [{"step": 1, "action": "click"}]
