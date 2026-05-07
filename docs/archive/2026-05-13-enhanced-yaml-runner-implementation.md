# Enhanced YAML Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor and enhance `src/yaml_runner.py` into a class-based executor with parameter injection and verification support.

**Architecture:** A `YAMLRunner` class manages the Playwright lifecycle, script injection, and step execution. It uses recursion for parameter replacement and Playwright's `expect` for assertions.

**Tech Stack:** Python 3.12+, Playwright, PyYAML, Pytest.

---

### Task 1: Refactor to YAMLRunner Class

**Files:**
- Modify: `src/yaml_runner.py`
- Test: `tests/test_yaml_runner.py`

- [ ] **Step 1: Write a basic test for YAMLRunner initialization**

```python
from src.yaml_runner import YAMLRunner

def test_runner_initialization():
    runner = YAMLRunner(headless=True)
    assert runner.headless is True
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_yaml_runner.py`
Expected: FAIL (ImportError or AttributeError)

- [ ] **Step 3: Refactor `src/yaml_runner.py` into a class**

```python
import yaml
import os
import re
from playwright.sync_api import sync_playwright, expect

class YAMLRunner:
    def __init__(self, headless=True):
        self.headless = headless
        self.axe_script = ""
        self.patch_script = ""
        self._load_scripts()

    def _load_scripts(self):
        # Handle cases where axe.min.js or a11y_patch.js might be missing during testing
        axe_path = os.path.join(os.path.dirname(__file__), 'axe.min.js')
        patch_path = os.path.join(os.path.dirname(__file__), 'a11y_patch.js')
        
        if os.path.exists(axe_path):
            with open(axe_path, 'r') as f:
                self.axe_script = f.read()
        if os.path.exists(patch_path):
            with open(patch_path, 'r') as f:
                self.patch_script = f.read()

    def _inject_scripts(self, context):
        if self.axe_script:
            context.add_init_script(self.axe_script)
        if self.patch_script:
            context.add_init_script(self.patch_script)

    def run_yaml(self, yaml_path, parameters=None):
        if not os.path.exists(yaml_path):
            print(f"Error: YAML file not found at {yaml_path}")
            return

        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            self._inject_scripts(context)
            page = context.new_page()
            
            for step in config.get('steps', []):
                processed_step = self._apply_parameters(step, parameters)
                self._execute_step(page, processed_step)
            
            browser.close()

    def _apply_parameters(self, step, parameters):
        # Placeholder for Task 2
        return step

    def _execute_step(self, page, step):
        # Placeholder for Task 3
        pass
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_yaml_runner.py`

- [ ] **Step 5: Commit**
`git add src/yaml_runner.py tests/test_yaml_runner.py && git commit -m "refactor: convert yaml_runner to class"`

---

### Task 2: Implement Parameter Injection

**Files:**
- Modify: `src/yaml_runner.py`
- Test: `tests/test_yaml_runner.py`

- [ ] **Step 1: Write tests for `_apply_parameters`**

```python
def test_apply_parameters():
    runner = YAMLRunner()
    params = {"id": "123", "name": "Test"}
    step = {"action": "fill", "label": "ID {{ id }}", "value": "{{ name }}"}
    
    processed = runner._apply_parameters(step, params)
    assert processed["label"] == "ID 123"
    assert processed["value"] == "Test"

def test_apply_parameters_missing_key():
    runner = YAMLRunner()
    params = {"id": "123"}
    step = {"action": "fill", "label": "ID {{ missing }}"}
    
    processed = runner._apply_parameters(step, params)
    assert processed["label"] == "ID {{ missing }}"
```

- [ ] **Step 2: Implement `_apply_parameters`**

```python
    def _apply_parameters(self, step, parameters):
        if parameters is None:
            return step
        
        def replace_match(match):
            key = match.group(1).strip()
            return str(parameters.get(key, match.group(0)))

        def process_value(val):
            if isinstance(val, str):
                return re.sub(r'\{\{(.*?)\}\}', replace_match, val)
            elif isinstance(val, list):
                return [process_value(v) for v in val]
            elif isinstance(val, dict):
                return {k: process_value(v) for k, v in val.items()}
            return val

        return process_value(step)
```

- [ ] **Step 3: Run tests to verify they pass**
Run: `pytest tests/test_yaml_runner.py`

- [ ] **Step 4: Commit**
`git commit -am "feat: implement parameter injection in YAMLRunner"`

---

### Task 3: Implement Actions and Verification

**Files:**
- Modify: `src/yaml_runner.py`
- Test: `tests/test_yaml_runner.py`

- [ ] **Step 1: Write integration tests for actions (using a local server or mocks)**

```python
import pytest
from playwright.sync_api import Page
from src.yaml_runner import YAMLRunner

def test_execute_step_goto(page: Page):
    runner = YAMLRunner()
    # goto action
    runner._execute_step(page, {"action": "goto", "url": "about:blank"})
    assert page.url == "about:blank"

def test_execute_step_verify_url(page: Page):
    runner = YAMLRunner()
    page.goto("about:blank")
    runner._execute_step(page, {"action": "verify", "type": "url", "value": "about:blank"})

def test_execute_step_verify_text(page: Page):
    runner = YAMLRunner()
    page.set_content("<div>Hello World</div>")
    runner._execute_step(page, {"action": "verify", "type": "text", "value": "Hello World"})
```

- [ ] **Step 2: Implement `_execute_step`**

```python
    def _execute_step(self, page, step):
        action = step.get('action')
        try:
            if action == 'goto':
                page.goto(step['url'])
            elif action == 'fill':
                page.get_by_label(step['label']).fill(step['value'])
            elif action == 'select':
                page.get_by_label(step['label']).select_option(step['value'])
            elif action == 'click':
                if 'label' in step:
                    page.get_by_label(step['label']).click()
                else:
                    page.get_by_text(step['text']).click()
            elif action == 'wait':
                page.wait_for_timeout(step.get('ms', 2000))
            elif action == 'verify':
                if step['type'] == 'url':
                    expect(page).to_have_url(step['value'])
                elif step['type'] == 'text':
                    expect(page.get_by_text(step['value'])).to_be_visible()
        except Exception as e:
            print(f"❌ Error during step {step}: {e}")
            raise
```

- [ ] **Step 3: Run all tests**
Run: `pytest tests/test_yaml_runner.py`

- [ ] **Step 4: Commit**
`git commit -am "feat: implement actions and verification in YAMLRunner"`
