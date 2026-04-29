import asyncio
import os
import sys

from src.runner import run_explorer
from src.generator import generate_script

async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Please set the GEMINI_API_KEY environment variable.")
        sys.exit(1)

    task = "Go to http://localhost:4200. Find employee ID 123. Under Benefits Enrollment, change Medical Coverage to 'Platinum Medical' and submit updates."
    print(f"Task: {task}")
    
    print("Running Browser-Use Agent...")
    history = await run_explorer(task)
    
    print("Agent finished. Generating Playwright script...")
    # Pass string representation of the history to the LLM
    history_str = str(history)
    
    params = {"employee_id": "123", "benefit_type": "Platinum Plan"}
    output_path = "generated_test.py"
    
    generate_script(history_str, params, output_path)
    
    print(f"\n✅ Generated parameterized Playwright script saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
