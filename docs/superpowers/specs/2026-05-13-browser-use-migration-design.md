# Design Spec: Migration from LaVague to Browser-Use

**Date:** 2026-05-13
**Status:** Draft
**Goal:** Replace the outdated LaVague framework with the modern, actively maintained `browser-use` library while preserving the existing YAML-based tool generation and execution workflow.

## 1. Objectives
- Replace `lavague` dependencies with `browser-use` and `langchain-google-genai`.
- Refactor the entire "Discovery & Freeze" pipeline to be asynchronous (`async/await`).
- Implement a `HistoryAdapter` to maintain compatibility with the legacy `Hardener` JSON format.
- Modernize `YAMLRunner` to use Playwright's async API.

## 2. Architecture

### 2.1 Component Overview
- **Explorer (Async)**: Uses `browser_use.Agent` to navigate and explore. It captures the agent's history and passes it to the adapter.
- **HistoryAdapter (Utility)**: A translation layer inside `Explorer` that converts `browser-use` steps into the format expected by the `Hardener`.
- **Hardener (Async)**: Processes the adapted logs to stabilize locators and parameterize the tool. Uses `ChatGoogleGenerativeAI` for LLM tasks.
- **YAMLRunner (Async)**: Executes the final `actions.yaml` using Playwright's `async_api`.

### 2.2 Data Flow
1. **Explore**: `Explorer.run_task` -> `browser-use` Agent -> Native History.
2. **Adapt**: Native History -> `HistoryAdapter` -> Legacy JSON Logs.
3. **Harden**: Legacy JSON Logs -> `Hardener.harden` -> `actions.yaml`.
4. **Execute**: `actions.yaml` -> `YAMLRunner.run` -> Final browser state.

## 3. Technical Specifications

### 3.1 Mapping Strategy (HistoryAdapter)
| browser-use Action | Legacy Action | Notes |
|-------------------|---------------|-------|
| `click_element`   | `click`       | Extract text or locator label. |
| `input_text`      | `fill`        | Extract label and value. |
| `open_url`        | `goto`        | Use URL from action. |
| `result.success`  | `success`     | Map boolean status. |

### 3.2 Async Migration
- **Explorer**: `async def run_task(self, url, goal)`.
- **Hardener**: `async def harden(self, goal, logs)`.
- **YAMLRunner**: `async def run(self, yaml_path, parameters)`.
- **Entry Point**: `asyncio.run(main())` in `run_lavague_demo.py` (to be renamed to `run_discovery_demo.py`).

## 4. Implementation Plan (High Level)
1. **Dependency Shift**: Update `pyproject.toml`, remove `lavague`, add `browser-use`, `langchain-google-genai`.
2. **Core Refactor**: Implement `Explorer` rewrite and `HistoryAdapter`.
3. **Pipeline Modernization**: Refactor `Hardener` and `YAMLRunner` to `async`.
4. **Verification**: Update unit tests and run E2E demo on Netlify HR system.

## 5. Testing
- **Unit Tests**: Update `tests/test_explorer.py`, `tests/test_hardener.py`, and `tests/test_yaml_runner.py` to use `pytest-asyncio`.
- **E2E**: Verify that `Update employee ID 3` still works with the new engine.
