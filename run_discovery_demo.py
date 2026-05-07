import asyncio
import os
import yaml
import json
from src.explorer import Explorer
from src.hardener import Hardener
from src.yaml_runner import YAMLRunner

async def main():
    print("--- 🚀 Starting Full Discovery Pipeline Demo ---")
    
    # 1. Initialize Discovery
    url = "https://hr-management-system1.netlify.app/dashboard"
    goal = "Update employee ID 3: change their department to 'Engineering' and position to 'DevOps Lead'"
    
    print(f"Goal: {goal}")
    print("Step 1: Running Explorer to discover steps...")
    
    explorer = Explorer()
    history = await explorer.run_task(url, goal)
    
    print(f"Explorer finished. Captured {len(history)} steps.")
    
    # 2. Harden the history
    print("Step 2: Hardening and parameterizing the captured history...")
    hardener = Hardener(context=explorer)
    tool = await hardener.harden(goal, history)
    
    # 3. Save to YAML
    yaml_path = "generated_actions.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(tool, f, sort_keys=False)
    
    print(f"Step 3: YAML saved to {yaml_path}")
    print(f"Detected Parameters: {[p['name'] for p in tool.get('parameters', [])]}")
    
    # 4. Re-run with the YAML Runner
    print("Step 4: Re-running with YAMLRunner to verify repeatability...")
    
    # Define parameters for execution (overriding defaults if necessary)
    # The hardener should have detected employee_id, department, and position
    parameters = {
        "employee_id": "3",
        "department": "Engineering",
        "position": "DevOps Lead"
    }
    
    runner = YAMLRunner(headless=True) # Use headless for verification
    success = await runner.run(yaml_path, parameters)
    
    if success:
        print("\n✅ Pipeline verified successfully!")
    else:
        print("\n❌ Pipeline verification failed.")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable is not set.")
    else:
        asyncio.run(main())
