# LLM Parameterization & Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement LLM-driven parameterization of browser actions and automatic success verification detection in the Hardener.

**Architecture:** 
- `Hardener` uses `GeminiContext` to access LLM capabilities.
- `parameterize` method sends the goal and history to Gemini, receiving a JSON mapping of parameters and templated steps.
- `detect_verification` analyzes the final steps of a trace for URL changes or "Success" text to add an explicit `verify` action.

**Tech Stack:** Python, LaVague (GeminiContext), LangChain, Pytest.

---

### Task 1: Update Hardener Initialization

**Files:**
- Modify: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Update `Hardener` class to accept `context`**

```python
class Hardener:
    def __init__(self, context=None):
        self.context = context
```

- [ ] **Step 2: Update existing tests to handle the new `__init__` (if necessary)**
Actually, since it's optional, existing tests should pass.

- [ ] **Step 3: Commit**

```bash
git add src/hardener.py
git commit -m "feat: add context support to Hardener"
```

### Task 2: Implement Success Evidence Detection

**Files:**
- Modify: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Write test for `detect_verification`**

```python
def test_detect_verification_url_change():
    hardener = Hardener()
    history = [
        {"action": "goto", "url": "http://app.com/form", "success": True},
        {"action": "click", "text": "Submit", "success": True, "url": "http://app.com/success"}
    ]
    verified = hardener.detect_verification(history)
    assert len(verified) == 3
    assert verified[-1]["action"] == "verify"
    assert verified[-1]["type"] == "url"
    assert verified[-1]["value"] == "http://app.com/success"

def test_detect_verification_success_text():
    hardener = Hardener()
    history = [
        {"action": "click", "text": "Submit", "success": True, "element_html": "<div>Successfully saved</div>"}
    ]
    verified = hardener.detect_verification(history)
    assert verified[-1]["action"] == "verify"
    assert verified[-1]["type"] == "text"
    assert "Successfully" in verified[-1]["value"]
```

- [ ] **Step 2: Implement `detect_verification` in `src/hardener.py`**

```python
    def detect_verification(self, history):
        if not history:
            return history
        
        last_step = history[-1]
        # Check URL change
        first_url = next((s.get("url") for s in history if s.get("url")), None)
        last_url = last_step.get("url")
        
        if last_url and first_url and last_url != first_url:
            history.append({
                "action": "verify",
                "type": "url",
                "value": last_url
            })
            return history

        # Check for success text in HTML or instruction
        success_keywords = ["success", "saved", "complete", "thank you", "confirmed"]
        html = last_step.get("element_html", "").lower()
        instruction = last_step.get("instruction", "").lower()
        
        for kw in success_keywords:
            if kw in html or kw in instruction:
                # Extract snippet
                value = kw.capitalize() # Simplified for now
                if kw in html:
                    value = last_step.get("element_html") # Or a snippet
                
                history.append({
                    "action": "verify",
                    "type": "text",
                    "value": value
                })
                break
        
        return history
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_hardener.py`

- [ ] **Step 4: Commit**

```bash
git add src/hardener.py tests/test_hardener.py
git commit -m "feat: implement success verification detection"
```

### Task 3: Implement LLM Parameterization

**Files:**
- Modify: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Write test for `parameterize` (mocking LLM)**

```python
from unittest.mock import MagicMock

def test_parameterize_basic():
    mock_context = MagicMock()
    mock_llm = MagicMock()
    mock_context.llm = mock_llm
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = """
    {
        "parameters": [
            {"name": "emp_id", "default": "123", "description": "Employee ID"}
        ],
        "steps": [
            {"action": "fill", "label": "ID", "value": "{{emp_id}}"}
        ]
    }
    """
    mock_llm.invoke.return_value = mock_response
    
    hardener = Hardener(context=mock_context)
    goal = "Update employee 123"
    history = [{"action": "fill", "label": "ID", "value": "123"}]
    
    result = hardener.parameterize(goal, history)
    
    assert len(result["parameters"]) == 1
    assert result["parameters"][0]["name"] == "emp_id"
    assert result["steps"][0]["value"] == "{{emp_id}}"
```

- [ ] **Step 2: Implement `parameterize` in `src/hardener.py`**

```python
import json

    def parameterize(self, goal, history):
        if not self.context or not self.context.llm:
            return {"parameters": [], "steps": history}
            
        prompt = f"""
        You are an automation expert. Analyze the user goal and the sequence of actions.
        Identify values in the actions that are derived from the goal and should be parameterized.
        
        User Goal: {goal}
        Actions: {json.dumps(history, indent=2)}
        
        Output ONLY a JSON object with:
        - "parameters": list of {{"name": "variable_name", "default": "original_value", "description": "brief description"}}
        - "steps": the actions with parameterized values replaced by {{{{variable_name}}}}
        """
        
        response = self.context.llm.invoke(prompt)
        # Handle both string and list content if necessary
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(content)
        except:
            # Fallback
            return {"parameters": [], "steps": history}
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_hardener.py`

- [ ] **Step 4: Commit**

```bash
git add src/hardener.py tests/test_hardener.py
git commit -m "feat: implement LLM-driven parameterization"
```

### Task 4: Final Integration

**Files:**
- Modify: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Add a convenience method `harden(goal, logs)` that orchestrates everything**

```python
    def harden(self, goal, logs):
        filtered = self.filter_history(logs)
        semantic = [self.map_to_semantic(s) for s in filtered]
        verified = self.detect_verification(semantic)
        parameterized = self.parameterize(goal, verified)
        return parameterized
```

- [ ] **Step 2: Add test for `harden`**

- [ ] **Step 3: Commit**

```bash
git add src/hardener.py
git commit -m "feat: add unified harden method"
```
