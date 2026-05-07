# Implement "Golden Path" Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `run_task` in `Explorer` class to execute a web task and return its execution logs.

**Architecture:** Use `lavague` components (`SeleniumDriver`, `ActionEngine`, `WorldModel`, `WebAgent`) to navigate to a URL and perform a goal, then return the logs.

**Tech Stack:** Python, `lavague` (Selenium, Gemini, Core)

---

### Task 1: Research and Setup

**Files:**
- Modify: `src/explorer.py`
- Modify: `tests/test_explorer.py`

- [ ] **Step 1: Verify `lavague` package availability and correct import paths**
Check what's installed in the venv and if the imports work.

### Task 2: Implement `run_task` with TDD

**Files:**
- Modify: `src/explorer.py`
- Modify: `tests/test_explorer.py`

- [ ] **Step 1: Write the failing test for `run_task`**

```python
import pytest
from unittest.mock import MagicMock, patch
from src.explorer import Explorer

# ... existing tests ...

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_explorer.py`
Expected: FAIL with `AttributeError: 'Explorer' object has no attribute 'run_task'`

- [ ] **Step 3: Implement `run_task` in `src/explorer.py`**

```python
from lavague.contexts.gemini import GeminiContext
from lavague.drivers.selenium import SeleniumDriver
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent

class Explorer:
    def __init__(self, model_name="models/gemini-1.5-flash"):
        self.context = GeminiContext(llm=model_name)

    def run_task(self, url: str, goal: str):
        # Initialize headless driver and components
        driver = SeleniumDriver(headless=True)
        action_engine = ActionEngine.from_context(self.context, driver)
        world_model = WorldModel.from_context(self.context)
        agent = WebAgent(world_model, action_engine)
        
        # Execute task
        agent.get(url)
        agent.run(goal)
        
        # Capture history and cleanup
        history = agent.logger.logs
        driver.driver.quit()
        return history
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_explorer.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/explorer.py tests/test_explorer.py
git commit -m "feat: implement run_task in Explorer for golden path capture"
```
