# Browser-Use to Playwright Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a system that translates a `browser-use` agent's successful action history into a parameterized Playwright script, along with a mock Angular HR app for testing.

**Architecture:** A Dual-Agent workflow with an Explorer (browser-use) that navigates a local Mock Angular application. A Coder LLM then translates the successful history into reusable Playwright code.

**Tech Stack:** Python, Playwright, browser-use, LangChain (or openai client), Node.js/Express, SQLite, Angular.

---

### Task 1: Initialize Python Project and Filter Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `src/runner.py`
- Create: `src/generator.py`
- Create: `src/filter.py`
- Test: `tests/test_filter.py`

- [ ] **Step 1: Write requirements.txt**
```text
browser-use
playwright
openai
pytest
```

- [ ] **Step 2: Initialize basic filter test**
```python
# tests/test_filter.py
def test_filter_removes_errors():
    from src.filter import filter_history
    raw_history = [{"action": "click", "success": False}, {"action": "fill", "success": True}]
    result = filter_history(raw_history)
    assert len(result) == 1
    assert result[0]["action"] == "fill"
```

- [ ] **Step 3: Run test to verify it fails**
Run: `pytest tests/test_filter.py -v`
Expected: FAIL (ModuleNotFoundError for src.filter)

- [ ] **Step 4: Write minimal filter implementation**
```python
# src/filter.py
def filter_history(history):
    return [step for step in history if step.get("success", False)]
```

- [ ] **Step 5: Write empty runner and generator files**
```python
# src/runner.py
def run_explorer(task: str, url: str):
    pass

# src/generator.py
def generate_script(filtered_history: list, params: dict):
    pass
```

- [ ] **Step 6: Run test to verify it passes**
Run: `pytest tests/test_filter.py -v`
Expected: PASS

- [ ] **Step 7: Commit**
```bash
git add requirements.txt src/ tests/
git commit -m "feat: initialize python project and filter scaffold"
```

### Task 2: Scaffold Mock Angular App & Backend

**Files:**
- Create: `mock-app/backend/server.js`
- Create: `mock-app/backend/package.json`

- [ ] **Step 1: Initialize backend package.json**
```json
{
  "name": "mock-hr-backend",
  "version": "1.0.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6",
    "cors": "^2.8.5"
  }
}
```

- [ ] **Step 2: Write minimal Express+SQLite backend**
```javascript
// mock-app/backend/server.js
const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const app = express();

app.use(cors());
app.use(express.json());

const db = new sqlite3.Database(':memory:');
db.serialize(() => {
    db.run("CREATE TABLE employees (id TEXT PRIMARY KEY, dental TEXT)");
    db.run("INSERT INTO employees VALUES ('123', 'Basic Plan')");
});

app.get('/api/employee/:id', (req, res) => {
    db.get("SELECT * FROM employees WHERE id = ?", [req.params.id], (err, row) => {
        res.json(row || { error: 'Not found' });
    });
});

app.post('/api/employee/:id/dental', (req, res) => {
    db.run("UPDATE employees SET dental = ? WHERE id = ?", [req.body.dental, req.params.id], () => {
        res.json({ success: true });
    });
});

app.listen(3000, () => console.log('Mock HR backend running on port 3000'));
```

- [ ] **Step 3: Commit**
```bash
git add mock-app/
git commit -m "feat: mock express backend for hr app"
```

### Task 3: Scaffold Angular Frontend

**Files:**
- Modify: `mock-app/frontend` (Angular CLI generation)

- [ ] **Step 1: Generate Angular app**
Run: `npx -y @angular/cli@17 new frontend --directory mock-app/frontend --defaults --skip-git`
Expected: Angular project created.

- [ ] **Step 2: Create Employee component**
Run: `cd mock-app/frontend && npx ng generate component employee`
Expected: Employee component created.

- [ ] **Step 3: Replace app.component.html**
```html
<!-- mock-app/frontend/src/app/app.component.html -->
<main>
  <h1>HR Portal</h1>
  <app-employee></app-employee>
</main>
```

- [ ] **Step 4: Commit**
```bash
git add mock-app/frontend/
git commit -m "feat: scaffold angular frontend"
```

### Task 4: Implement Generator LLM Call

**Files:**
- Modify: `src/generator.py`

- [ ] **Step 1: Implement generate_script**
```python
# src/generator.py
import os
from openai import OpenAI

def generate_script(filtered_history: list, params: dict, output_path: str):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = f"""
    You are a Playwright expert. Convert this agent history into a Python Playwright script.
    Use robust locators (getByText, getByRole).
    Replace these hardcoded values with parameters: {params}.
    History: {filtered_history}
    Output ONLY python code.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    code = response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
    
    with open(output_path, "w") as f:
        f.write(code)
```

- [ ] **Step 2: Commit**
```bash
git add src/generator.py
git commit -m "feat: implement code generator using openai"
```

### Task 5: Implement Browser-Use Runner

**Files:**
- Modify: `src/runner.py`

- [ ] **Step 1: Implement run_explorer**
```python
# src/runner.py
import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI

async def run_explorer(task: str):
    llm = ChatOpenAI(model="gpt-4o")
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    return history
```

- [ ] **Step 2: Commit**
```bash
git add src/runner.py
git commit -m "feat: implement browser-use runner"
```
