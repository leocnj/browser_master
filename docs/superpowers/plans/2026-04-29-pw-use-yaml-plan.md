# Implementation Plan: Data-Driven Playwright & A11y Patching (feat/pw_use_yaml)

## Task 1: Environment Setup
**Target:** `pyproject.toml` / Virtual Environment
- **Action**: Add `PyYAML` to the project dependencies to enable parsing the `actions.yaml` file.

## Task 2: Develop Dynamic A11y Polyfill Script
**File:** `src/a11y_patch.js`
- **Action**: Write a JavaScript script that defines a function `patchHostileInputs()`. This function will query all `<input>` and `<select>` elements.
- **Action**: For any input lacking an `id` or `aria-label`, find the closest preceding text node or text span (e.g., `<span class="text-label">Medical Coverage:</span>`) and assign its text content to the input's `aria-label`.
- **Action**: Set up a `MutationObserver` on `document.body` that listens for child node additions and re-runs `patchHostileInputs()` when the DOM mutates.

## Task 3: Build the YAML Execution Engine
**File:** `src/yaml_runner.py`
- **Action**: Create a `playwright.sync_api` function that loads a given `actions.yaml` file using the `yaml` library.
- **Action**: Read `src/a11y_patch.js` and inject it into the browser context using `page.add_init_script()`.
- **Action**: Implement a loop that iterates through the YAML steps, performing:
    - `goto`: `page.goto(step['url'])`
    - `fill`: `page.get_by_label(step['label']).fill(step['value'])`
    - `select`: `page.get_by_label(step['label']).select_option(step['value'])`
    - `click`: `page.get_by_text(step['text']).click()`

## Task 4: Define the YAML Workflow
**File:** `actions.yaml`
- **Action**: Define the exact sequence to navigate the mock HR app:
    1. Navigate to `http://localhost:4200`
    2. Fill label "Employee ID Lookup" with "123"
    3. Click "Search Profile"
    4. Select label "Medical Coverage:" with "Platinum Medical"
    5. Click "Submit Updates"

## Task 5: Integration & Verification
**File:** `run_yaml_demo.py` (New Orchestrator)
- **Action**: Create a simple script that invokes `yaml_runner.py` targeting `actions.yaml`.
- **Action**: Verify the execution visually to confirm the hostile DOM is successfully navigated using purely semantic labels.
