import os
from openai import OpenAI

def generate_script(filtered_history: list, params: dict, output_path: str):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    code = response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
    
    with open(output_path, "w") as f:
        f.write(code)
