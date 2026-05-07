# Hardener - Noise Filtering & A11y Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a Hardener class that filters successful interaction steps and maps technical locators (XPaths) to semantic ones (labels/text) using instruction hints and HTML heuristics.

**Architecture:** A standalone class `Hardener` with methods for filtering and semantic mapping. It uses `BeautifulSoup` to parse `element_html` and find labels based on heuristics similar to `src/a11y_patch.js`.

**Tech Stack:** Python, BeautifulSoup4, Pytest.

---

### Task 1: Setup Hardener Class and Basic Filtering

**Files:**
- Create: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Write the failing test for filter_history**

```python
import pytest
from src.hardener import Hardener

def test_filter_history_removes_unsuccessful_steps():
    hardener = Hardener()
    logs = [
        {"action": "click", "success": True, "xpath": "/button[1]"},
        {"action": "fill", "success": False, "xpath": "/input[1]"},
        {"action": "click", "success": True, "xpath": "/button[2]"}
    ]
    filtered = hardener.filter_history(logs)
    assert len(filtered) == 2
    assert all(step["success"] for step in filtered)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_hardener.py -v`
Expected: ModuleNotFoundError or FAIL

- [ ] **Step 3: Implement Hardener class and filter_history**

```python
class Hardener:
    def filter_history(self, logs):
        """
        Only keep steps where the action was successful.
        Flattens the logs into a clean list of interaction steps.
        """
        if not logs:
            return []
        # Basic filtering for success
        return [step for step in logs if step.get("success", False)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_hardener.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hardener.py tests/test_hardener.py
git commit -m "feat: add Hardener class and filter_history"
```

### Task 2: Implement Semantic Mapping via Instruction

**Files:**
- Modify: `src/hardener.py`
- Modify: `tests/test_hardener.py`

- [ ] **Step 1: Write test for instruction-based mapping**

```python
def test_map_to_semantic_uses_instruction():
    hardener = Hardener()
    step = {
        "action": "click",
        "xpath": "//button[1]",
        "instruction": "Click Search",
        "success": True
    }
    mapped = hardener.map_to_semantic(step)
    assert mapped["action"] == "click"
    assert mapped["text"] == "Search"
    assert "xpath" not in mapped
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_hardener.py -v`
Expected: AttributeError (map_to_semantic not implemented)

- [ ] **Step 3: Implement map_to_semantic (instruction part)**

```python
    def map_to_semantic(self, step):
        new_step = step.copy()
        action = new_step.get("action")
        instruction = new_step.get("instruction", "")

        if action == "click" and "Click " in instruction:
            label = instruction.replace("Click ", "").strip()
            new_step["text"] = label
            if "xpath" in new_step:
                del new_step["xpath"]
        
        return new_step
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_hardener.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hardener.py tests/test_hardener.py
git commit -m "feat: implement instruction-based semantic mapping"
```

### Task 3: Implement Semantic Mapping via HTML Heuristics

**Files:**
- Modify: `src/hardener.py`
- Modify: `tests/test_hardener.py`

- [ ] **Step 1: Write test for HTML-based mapping**

```python
def test_map_to_semantic_uses_html_heuristics():
    hardener = Hardener()
    step = {
        "action": "fill",
        "xpath": "//input[@id='user']",
        "element_html": "<div><label>Username:</label><input id='user'></div>",
        "value": "alice",
        "success": True
    }
    mapped = hardener.map_to_semantic(step)
    assert mapped["action"] == "fill"
    assert mapped["label"] == "Username"
    assert mapped["value"] == "alice"
    assert "xpath" not in mapped
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_hardener.py -v`
Expected: FAIL (label "Username" not found)

- [ ] **Step 3: Implement HTML heuristic label detection**

```python
from bs4 import BeautifulSoup

class Hardener:
    # ... existing filter_history ...

    def _find_label_in_html(self, html_snippet, target_xpath=None):
        soup = BeautifulSoup(html_snippet, 'html.parser')
        
        # Simple heuristic: find the first label or text before an input
        # In a real scenario, we'd use the xpath to find the specific element.
        # For this task, we'll try to find common patterns.
        
        # Strategy 1: <label> text
        label_tag = soup.find('label')
        if label_tag:
            return label_tag.get_text().strip().replace(":", "")
            
        # Strategy 2: text in preceding sibling or parent's first child
        # (Simplified version of a11y_patch.js logic)
        inputs = soup.find_all(['input', 'select', 'textarea', 'button'])
        for inp in inputs:
            # Check previous sibling
            prev = inp.find_previous_sibling()
            if prev and prev.get_text().strip():
                return prev.get_text().strip().replace(":", "")
            
            # Check parent's first child if it's not the input itself
            parent = inp.parent
            if parent and parent.contents:
                first = parent.contents[0]
                if hasattr(first, 'get_text') and first.get_text().strip():
                    return first.get_text().strip().replace(":", "")
                elif isinstance(first, str) and first.strip():
                    return first.strip().replace(":", "")
        
        return None

    def map_to_semantic(self, step):
        new_step = step.copy()
        action = new_step.get("action")
        instruction = new_step.get("instruction", "")
        html = new_step.get("element_html", "")

        # Try instruction first
        label = None
        if "Click " in instruction:
            label = instruction.replace("Click ", "").strip()
        elif "Fill " in instruction:
            # e.g. "Fill Username with alice"
            parts = instruction.replace("Fill ", "").split(" with ")
            if len(parts) > 0:
                label = parts[0].strip()

        # Try HTML heuristics if instruction didn't yield a good label
        if not label and html:
            label = self._find_label_in_html(html)

        if label:
            if action == "click":
                new_step["text"] = label
            else:
                new_step["label"] = label
            
            if "xpath" in new_step:
                del new_step["xpath"]
        
        return new_step
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_hardener.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hardener.py tests/test_hardener.py
git commit -m "feat: implement HTML-based semantic mapping"
```

### Task 4: Final Verification and Cleanup

**Files:**
- Modify: `src/hardener.py`
- Modify: `tests/test_hardener.py`

- [ ] **Step 1: Add a comprehensive test case**

```python
def test_hardener_process_full_logs():
    hardener = Hardener()
    logs = [
        {"action": "goto", "url": "http://app.com", "success": True},
        {"action": "fill", "instruction": "Fill Email with test@test.com", "xpath": "//input[1]", "success": True, "value": "test@test.com"},
        {"action": "click", "element_html": "<button>Login</button>", "xpath": "//button[1]", "success": True},
        {"action": "click", "xpath": "//bad", "success": False}
    ]
    
    filtered = hardener.filter_history(logs)
    hardened = [hardener.map_to_semantic(s) for s in filtered]
    
    assert len(hardened) == 3
    assert hardened[1]["label"] == "Email"
    assert hardened[2]["text"] == "Login"
    assert "xpath" not in hardened[1]
    assert "xpath" not in hardened[2]
```

- [ ] **Step 2: Run all tests**

Run: `pytest tests/test_hardener.py -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_hardener.py
git commit -m "test: add full log hardening test"
```
