# Gemini-Optimized Discovery & Freeze (LaVague + YAML) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous pipeline that uses Google Gemini (via LaVague) to explore a hosted HR system and "freeze" successful interactions into deterministic, parameterized YAML tools.

**Architecture:** 3-stage pipeline: (1) LaVague Explorer (Gemini), (2) LLM Hardener (Parameterization + A11y Mapping), (3) YAML Runner (Execution + Verification).

**Tech Stack:** Python, LaVague (Gemini Context), Playwright, PyYAML, Jinja2.

---

### Task 1: Initialize LaVague Explorer
**Files:**
- Create: `src/explorer.py`
- Test: `tests/test_explorer.py`

- [ ] **Step 1: Write a test to initialize LaVague with Gemini**
```python
import pytest
from src.explorer import Explorer

def test_explorer_initialization():
    explorer = Explorer(model_name="gemini-1.5-flash")
    assert explorer.context is not None
```
- [ ] **Step 2: Implement basic Explorer class**
- [ ] **Step 3: Run test and verify**
- [ ] **Step 4: Commit**

### Task 2: Implement "Golden Path" Capture
**Files:**
- Modify: `src/explorer.py`
- Test: `tests/test_explorer.py`

- [ ] **Step 1: Add `run_task` method to Explorer that returns ActionHistory**
- [ ] **Step 2: Test it on a simple local page**
- [ ] **Step 3: Commit**

### Task 3: The Hardener - Noise Filtering & A11y Mapping
**Files:**
- Create: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Write test for filtering failed actions from history**
- [ ] **Step 2: Implement filtering logic**
- [ ] **Step 3: Implement A11y Mapping (mapping XPath to nearest label/text)**
- [ ] **Step 4: Commit**

### Task 4: LLM Parameterization & Verification
**Files:**
- Modify: `src/hardener.py`
- Test: `tests/test_hardener.py`

- [ ] **Step 1: Write test for parameter detection (comparing goal vs actions)**
- [ ] **Step 2: Implement LLM prompt for parameterization using Gemini**
- [ ] **Step 3: Implement Success Evidence detection (Assertions in YAML)**
- [ ] **Step 4: Commit**

### Task 5: Enhanced YAML Runner
**Files:**
- Modify: `src/yaml_runner.py`
- Test: `tests/test_yaml_runner.py`

- [ ] **Step 1: Update runner to support `verify` actions (Strict Verification)**
- [ ] **Step 2: Implement runtime A11y patching injection**
- [ ] **Step 3: Commit**

### Task 6: End-to-End Validation (Netlify HR System)
**Files:**
- Create: `run_lavague_demo.py`

- [ ] **Step 1: Create a script that runs the full pipeline on `https://hr-management-system1.netlify.app/dashboard`**
- [ ] **Step 2: Run discovery for "Update employee ID 2's job title"**
- [ ] **Step 3: Verify the generated `actions.yaml` is parameterized and deterministic**
- [ ] **Step 4: Commit and finalize**
