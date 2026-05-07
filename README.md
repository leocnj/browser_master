# Browser Master: Autonomous Discovery & Freeze Pipeline

An advanced web automation system that uses Google Gemini and LaVague to explore legacy web applications and "freeze" them into deterministic, parameterized YAML tools.

## Key Features

- **Autonomous Discovery**: Uses LaVague and Gemini 2.5 to explore "hostile" or legacy UIs and achieve high-level goals.
- **Surgical Hardening**: Automatically converts brittle XPaths to stable semantic labels and detects success evidence.
- **Deterministic Execution**: Replays captured flows using a high-performance Playwright runner with Jinja2 parameterization.
- **Legacy Resilience**: Injects `axe-core` and custom a11y patches at runtime to fix broken DOMs in real-time.

## Quick Start

### 1. Installation
```bash
uv sync
playwright install chromium
```

### 2. Run Discovery & Freeze Demo
```bash
export GOOGLE_API_KEY=your_key_here
uv run python run_lavague_demo.py
```

This will:
1. **Explore**: Navigate the Netlify HR system to update an employee.
2. **Harden**: Generate a parameterized `generated_actions.yaml`.
3. **Execute**: Re-run the task deterministically with new parameters.

## Architecture

- `src/explorer.py`: LaVague-based task exploration and SDK patching.
- `src/hardener.py`: LLM-driven semantic mapping and parameterization.
- `src/yaml_runner.py`: Deterministic Playwright execution engine.
- `src/a11y_patch.js`: Runtime accessibility remediation.

## Testing
```bash
uv run python -m pytest
```
