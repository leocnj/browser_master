# Design Spec: Data-Driven Playwright & A11y Patching (feat/pw_use_yaml)

## 1. Objective
Refactor the current hardcoded Playwright automation into a generic, data-driven execution engine using YAML. Furthermore, completely eliminate the need for brittle, complex XPath locators by dynamically "patching" the legacy Angular DOM at runtime with standard Accessibility (a11y) labels.

## 2. YAML-Driven Execution (Separation of Concerns)
Instead of generating Python code for every new workflow, the LLM will generate a structured YAML file defining the sequence of user actions. A single, generic Python engine will parse this file and execute the steps.

**Proposed `actions.yaml` Schema:**
```yaml
steps:
  - action: "goto"
    url: "http://localhost:4200"
  - action: "fill"
    label: "Employee ID Lookup" # Semantic label
    value: "123"
  - action: "click"
    text: "Search Profile"
  - action: "select"
    label: "Medical Coverage:" # Hostile element, but patched to be semantic!
    value: "Platinum Medical"
  - action: "click"
    text: "Submit Updates"
```
**Benefits**: The LLM output is strictly validated YAML. The execution code (`generic_runner.py`) is written once, maintained easily, and handles retries, waits, and logging generically.

## 3. Dynamic Accessibility Patching (Hostile DOM Remediation)
To allow the YAML to rely purely on readable, semantic `label`s (even for our hostile `<div>`-based elements), we will use Playwright's `page.add_init_script()` to inject a client-side JavaScript patch.

**The Strategy:**
1. **Heuristic A11y Polyfill**: The script will run immediately upon page load. It will scan for "hostile" inputs (e.g., `<input>` or `<select>` tags lacking an `id`, `name`, or `aria-label`).
2. **Sibling Text Association**: For every hostile input found, the script traverses the DOM to find the immediate preceding text node or `<span>` (e.g., `<span>Base Salary:</span>`).
3. **Dynamic Patching**: It takes the text content of that span and assigns it to the input's `aria-label` attribute (e.g., `<select aria-label="Base Salary:">`).
4. **Mutation Observer (Standard Tech)**: We will use the standard HTML5 `MutationObserver` API to ensure that if the Angular app dynamically renders *new* hostile elements later (like when data is fetched), those elements are instantly patched the millisecond they appear in the DOM.

## 4. Impact on the Architecture
* **Explorer Agent (`browser-use`)**: Can now interact with the legacy Angular app *perfectly* during the exploration phase because the DOM will be fully accessible!
* **Coder Agent (`generator.py`)**: Will be swapped to a YAML-generator prompt. Instead of outputting python code, it outputs the `actions.yaml` file based on the now-successful exploration history.
