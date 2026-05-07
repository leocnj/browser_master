import os
# Disable LaVague telemetry immediately
os.environ["LAVAGUE_TELEMETRY"] = "NONE"

import json
import yaml
from src.explorer import Explorer
from src.hardener import Hardener
from src.yaml_runner import YAMLRunner

def run_demo(goal, url, parameters=None):
    print(f"🚀 Starting Discovery & Freeze for goal: '{goal}'")
    
    # 1. Explorer Phase
    print("\n--- Phase 1: Exploration (LaVague) ---")
    explorer = Explorer()
    try:
        raw_logs = explorer.run_task(url, goal)
        print(f"✅ Exploration complete. Captured {len(raw_logs)} steps.")
    except Exception as e:
        print(f"❌ Exploration failed: {e}")
        return

    # 2. Hardener Phase
    print("\n--- Phase 2: Hardening & Parameterization ---")
    hardener = Hardener(context=explorer.context)
    hardened_data = hardener.harden(goal, raw_logs)
    
    yaml_path = "generated_actions.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(hardened_data, f, default_flow_style=False)
    
    print(f"✅ Hardening complete. Tool saved to {yaml_path}")
    print(f"Detected Parameters: {hardened_data.get('parameters', [])}")

    # 3. Execution Phase
    print("\n--- Phase 3: Deterministic Execution (YAMLRunner) ---")
    runner = YAMLRunner(headless=False)
    success = runner.run(yaml_path, parameters=parameters)
    
    if success:
        print("\n🎉 Full pipeline successful!")
    else:
        print("\n❌ Pipeline failed during execution phase.")

if __name__ == "__main__":
    # Example Target: Netlify HR System
    TARGET_URL = "https://hr-management-system1.netlify.app/dashboard"
    GOAL = "Update employee ID 3: change their department to 'Engineering' and position to 'DevOps Lead'"
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Warning: GOOGLE_API_KEY not set. Discovery phase will fail.")
        print("To run for real: export GOOGLE_API_KEY=your_key_here")
    
    # Run with different parameters to prove determinism
    run_demo(GOAL, TARGET_URL, parameters={
        "department": "Engineering",
        "position": "Senior DevOps Architect"
    })
