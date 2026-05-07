# Design Spec: Gemini-Optimized Discovery & Freeze (LaVague + YAML)

## 1. Objective
Build an autonomous pipeline that uses Google Gemini (via the LaVague framework) to explore "hostile" legacy web applications and "freeze" successful interactions into deterministic, parameterized YAML tools. This eliminates the brittleness of AI-only agents and the high cost of manual automation.

## 2. Architecture: The Three-Stage Pipeline

### Stage 1: The Explorer (LaVague)
- **Engine**: [LaVague](https://lavague.ai/) using `GeminiContext`.
- **Function**: Accepts a Natural Language goal (e.g., "Find employee 123 and update their medical plan to Platinum").
- **Gemini Advantage**: Leverages Gemini 1.5 Pro's 1M+ context window and visual reasoning to analyze complex DOMs that confuse smaller context models.
- **Output**: A raw `ActionHistory` list containing the sequence of successful and failed steps.

### Stage 2: The Hardener (Trace Refinement)
- **Noise Filtering**: Strips out failed retries, misclicks, and unnecessary scrolls from the LaVague history.
- **Semantic Mapping**: Uses the `a11y_patch.js` logic to map brittle CSS/XPaths used by the agent back to stable `aria-label` or `text` locators.
- **LLM Parameterization**: 
  - Uses Gemini 1.5 Flash to compare the original goal with the successful trace.
  - Automatically identifies variables (e.g., if "123" in the goal matches `fill(value="123")` in the trace, it creates `{{emp_id}}`).
- **Strict Verification**: Identifies the "Evidence of Success" (e.g., a "Saved" toast message) and adds it as a mandatory `wait_for` step in the final tool.

### Stage 3: The Executor (YAML Runner)
- **Engine**: Refactored `yaml_runner.py`.
- **Function**: Executes the `actions.yaml` file using Playwright.
- **Features**:
  - Handles variable injection (Jinja-style `{{parameter}}`).
  - Implements the accessibility patch at runtime to ensure semantic locators work on legacy DOMs.
  - Fail-fast logic if verification steps are not met.

## 3. Data Schema: `actions.yaml`
```yaml
version: "1.0"
metadata:
  name: "update_employee_benefits"
  description: "Updates benefits based on employee ID"
parameters:
  - name: "emp_id"
    default: "123"
  - name: "plan_name"
    default: "Platinum"
steps:
  - action: "goto"
    url: "http://localhost:4200"
  - action: "fill"
    label: "Employee ID Search"
    value: "{{emp_id}}"
  - action: "click"
    text: "Search"
  - action: "select"
    label: "Medical Coverage"
    value: "{{plan_name}}"
  - action: "verify"
    text: "Success: Benefits Updated"
```

## 4. Success Criteria
1. **Gemini Compatibility**: Pipeline must run using Gemini 1.5 Pro/Flash without failing due to model-specific reasoning errors.
2. **Determinism**: A generated YAML tool must succeed 100% of the time when re-run on the [Netlify HR Management System](https://hr-management-system1.netlify.app/dashboard).
3. **Parameterization**: The Hardener must correctly identify at least 2 parameters from a complex multi-step goal (e.g., updating a specific employee's details).
4. **Resilience**: The tool must work even if the internal DOM structure of the legacy app changes (as long as labels remain consistent).
