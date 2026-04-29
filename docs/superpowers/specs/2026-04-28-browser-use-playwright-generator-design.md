# Browser-Use to Playwright Generator

## Purpose
To create a system that uses the `browser-use` agentic framework to autonomously explore an Angular HR application, complete a specific task, and then automatically generate a deterministic, parameterized Python Playwright script representing the successful "golden path" of that task.

## Architecture

The system utilizes a Dual-Agent Workflow with two distinct phases:

1.  **Explorer Phase:** A Python script instantiates a `browser-use` `Agent` with a natural language task (e.g., "Find employee ID 123 and update their dental benefit to 'Premium Plan'"). The agent navigates the web application autonomously.
2.  **Coder Phase:** The system extracts the `AgentHistoryList` from the completed Explorer run. A custom History Filter function strips out failed actions, retries, and errors, isolating the successful sequence of actions. This "golden path" history, along with the expected parameter mapping, is passed to a Coder LLM which generates the final Playwright script.

## Components & Data Flow

1.  **Browser-Use Runner (`runner.py`):**
    *   Initializes the `browser-use` agent.
    *   Executes the natural language task on the target Angular application.
    *   Returns the `AgentHistoryList`.

2.  **History Filter (`filter.py`):**
    *   Parses the `AgentHistoryList`.
    *   Removes steps with errors or unsuccessful outcomes.
    *   Formats the successful actions into a JSON-serializable list of structured steps (action type, target element, input text).

3.  **Playwright Generator (`generator.py`):**
    *   Takes the filtered history and a parameter configuration (e.g., `{"employee_id": "123", "benefit_type": "Premium Plan"}`).
    *   Calls the Coder LLM.
    *   Prompts the LLM to map the raw actions to Playwright methods using robust Angular-friendly selectors (`getByText`, `getByRole`, etc.) instead of brittle CSS selectors.
    *   Outputs a standalone `.py` file containing the parameterized Playwright function.

## Parameterization
The system requires a parameter configuration dictionary provided before the Coder Phase. The Coder LLM uses this dictionary to identify hardcoded values in the Explorer's history (e.g., the string "123") and replace them with variable references (e.g., `employee_id`) in the generated Playwright function signature and body.

## Error Handling
*   If the Explorer agent fails to complete the task entirely, the system will abort the generation process and output the agent's failure reason.
*   The Coder LLM is strictly prompted to validate that all requested parameters are utilized in the generated script.
