# Initialize LaVague Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap LaVague `GeminiContext` in a clean `Explorer` class.

**Architecture:** Use `lavague.contexts.gemini.GeminiContext` to provide LLM capabilities to LaVague.

**Tech Stack:** Python, LaVague, Gemini.

---

### Task 1: Initialize LaVague Explorer

**Files:**
- Create: `src/explorer.py`
- Test: `tests/test_explorer.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from src.explorer import Explorer

def test_explorer_initialization():
    explorer = Explorer(model_name="gemini-1.5-flash")
    assert explorer.context is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_explorer.py -v`
Expected: FAIL (ModuleNotFoundError or ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
from lavague.contexts.gemini import GeminiContext

class Explorer:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.context = GeminiContext(llm=model_name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_explorer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/explorer.py tests/test_explorer.py
git commit -m "feat: initialize LaVague Explorer with GeminiContext"
```
