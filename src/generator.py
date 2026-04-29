import os
from langchain_google_genai import ChatGoogleGenerativeAI

def generate_script(filtered_history: list, params: dict, output_path: str):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    prompt = f"""
    You are a Playwright expert. Convert this agent history into a Python Playwright script.
    The target is a legacy Angular app with poor accessibility. Use this fallback hierarchy for locators:
    1. getByText()
    2. page.locator('[ng-reflect-*="..."]')
    3. XPath relative to nearby text
    4. .nth() as a last resort
    Do not assume getByRole or getByLabel will work.
    Replace these hardcoded values with parameters: {params}.
    History: {filtered_history}
    Output ONLY python code.
    """
    
    response = llm.invoke(prompt)
    
    code = response.content.replace("```python", "").replace("```", "").strip()
    
    with open(output_path, "w") as f:
        f.write(code)
