import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from src.explorer import Explorer
from pydantic import SecretStr

@pytest.mark.asyncio
async def test_explorer_initialization():
    with patch("src.explorer.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm
        
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            explorer = Explorer(model_name="gemini-2.0-flash-exp")
            
            mock_llm_cls.assert_called_once()
            args, kwargs = mock_llm_cls.call_args
            assert kwargs["model"] == "gemini-2.0-flash-exp"
            assert isinstance(kwargs["api_key"], SecretStr)
            assert kwargs["api_key"].get_secret_value() == "test-key"

@pytest.mark.asyncio
async def test_run_task_success():
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
        with patch("src.explorer.ChatGoogleGenerativeAI"), \
             patch("src.explorer.Agent") as mock_agent_cls:
            
            mock_agent = MagicMock()
            mock_agent_cls.return_value = mock_agent
            
            # Mocking the async run method
            mock_agent.run = AsyncMock()
            
            # Mocking history steps
            class MockAction:
                def __init__(self, name, params):
                    self.name = name
                    self.params = params

                def dict(self):
                    return {self.name: self.params}

            # Simulate browser-use history
            mock_history = MagicMock()
            mock_history.final_result.return_value = "Done"
            
            # Creating mock steps with actions
            step1 = MagicMock()
            step1.browser_action = MockAction("open_url", {"url": "https://example.com"})
            
            step2 = MagicMock()
            step2.browser_action = MockAction("click_element", {"index": 0})
            
            step3 = MagicMock()
            step3.browser_action = MockAction("input_text", {"index": 1, "text": "hello"})
            
            mock_history.history = [step1, step2, step3]
            mock_agent.run.return_value = mock_history
            
            explorer = Explorer()
            history = await explorer.run_task("https://example.com", "Goal")
            
            assert len(history) == 3
            assert history[0] == {"action": "goto", "url": "https://example.com", "success": True}
            assert history[1] == {"action": "click", "text": 0, "success": True}
            assert history[2] == {"action": "fill", "label": 1, "value": "hello", "success": True}

@pytest.mark.asyncio
async def test_map_to_legacy_actions():
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
        explorer = Explorer()
    
    class MockAction:
        def __init__(self, name, params):
            self.name = name
            self.params = params
        def dict(self):
            return {self.name: self.params}

    class MockStep:
        def __init__(self, name, params):
            self.browser_action = MockAction(name, params)

    # Test individual mappings
    step_goto = MockStep("open_url", {"url": "http://test.com"})
    assert explorer._map_to_legacy([step_goto]) == [{"action": "goto", "url": "http://test.com", "success": True}]
    
    step_click = MockStep("click_element", {"index": 5})
    assert explorer._map_to_legacy([step_click]) == [{"action": "click", "text": 5, "success": True}]
    
    step_fill = MockStep("input_text", {"index": "user", "text": "Alice"})
    assert explorer._map_to_legacy([step_fill]) == [{"action": "fill", "label": "user", "value": "Alice", "success": True}]
    
    step_unknown = MockStep("unknown_action", {"foo": "bar"})
    assert explorer._map_to_legacy([step_unknown]) == []
