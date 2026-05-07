# Enhanced YAML Runner Design

**Goal:** Refactor and enhance the YAML runner to support strict verification, parameter injection, and runtime A11y patching.

## Architecture
The `YAMLRunner` is a class-based executor for YAML-defined browser actions. It leverages Playwright for browser automation and incorporates a custom A11y patcher to improve locatability on inaccessible DOMs.

### YAMLRunner Class
- `__init__(self, headless=True)`: Initializes the runner with configuration options.
- `run_yaml(self, yaml_path, parameters=None)`: The main entry point. Loads the YAML, applies parameters, and executes steps.
- `_inject_scripts(self, context)`: Reads and injects `axe.min.js` and `a11y_patch.js`.
- `_apply_parameters(self, step, parameters)`: Recursively replaces `{{ key }}` placeholders in step definitions.
- `_execute_step(self, page, step)`: Executes a single action step.

## Features

### Parameter Injection
- Supports `{{ key }}` syntax in YAML action values.
- Replaces placeholders with values provided in the `parameters` dictionary.
- If a parameter is missing, a warning is logged, and the placeholder remains.

### Verification (Strict Mode)
- `action: "verify"`
- `type: "url"`: Asserts that the current page URL exactly matches the expected value.
- `type: "text"`: Asserts that the specified text is visible on the page, waiting for visibility if necessary.

### Runtime A11y Patching
- Automatically injects `axe.min.js` and `a11y_patch.js` before any navigation.
- Ensures `page.get_by_label()` and other semantic locators work on poorly structured pages.

### Supported Actions
- `goto`: Navigate to a URL.
- `fill`: Fill an input field identified by label.
- `click`: Click an element identified by label or text.
- `select`: Select an option in a dropdown identified by label.
- `wait`: Pause execution for a specified duration (ms).
- `verify`: Perform assertions on page state.

## Testing Strategy
- **Unit Tests**: Test `_apply_parameters` logic with various inputs and edge cases.
- **Integration Tests**: Use a mock or a real browser (if available in the test environment) to verify step execution, script injection, and `verify` actions.
- **Verification**: Use `pytest` with `playwright` fixtures if possible.

## Files
- `src/yaml_runner.py`: Implementation of `YAMLRunner`.
- `tests/test_yaml_runner.py`: Test suite for the runner.
- `src/a11y_patch.js`: (Existing) Patching logic.
- `src/axe.min.js`: (Existing) Accessibility engine.
