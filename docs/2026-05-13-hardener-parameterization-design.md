# Design: LLM Parameterization & Verification

## Architecture
Update `Hardener` to support LLM-driven parameterization and automatic verification detection.

### 1. Hardener Initialization
- Accept `context` (GeminiContext) in `__init__`.

### 2. Parameterization (`parameterize`)
- **Input**: `goal` (string), `hardened_history` (list of dicts).
- **Process**:
    - Construct a prompt for Gemini that includes the user goal and the sequence of semantic actions.
    - Ask Gemini to identify values in the actions that are derived from the goal.
    - Ask Gemini to return a JSON with:
        - `parameters`: List of `{"name": "...", "default": "...", "description": "..."}`.
        - `steps`: The original `hardened_history` but with values replaced by `{{name}}`.
- **Output**: A dictionary with `parameters` and `steps`.

### 3. Verification Detection (`detect_verification`)
- **Input**: `hardened_history` (list of dicts).
- **Process**:
    - Examine the last successful step in the history.
    - Check for `url` changes or "Success" indicators in `element_html` or `instruction`.
    - If found, add a final step: `{"action": "verify", "type": "...", "value": "..."}`.
- **Output**: Modified `hardened_history`.

## Testing Strategy
- **Unit Tests**:
    - Mock `GeminiContext` and its LLM to return controlled JSON responses.
    - Verify `parameterize` correctly handles the mapping.
    - Verify `detect_verification` identifies URL changes and success messages.
- **Integration Tests**:
    - Ensure `Hardener` works with real (or near-real) history objects from LaVague.

## Design Review Questions
- Should the `verify` step be part of the `steps` returned by `parameterize`, or a separate step in the workflow?
- I'll assume it's added to the history *before* parameterization so the LLM can also parameterize verification values if needed.
