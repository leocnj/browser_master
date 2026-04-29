from src.yaml_runner import run_yaml_steps

if __name__ == "__main__":
    print("🚀 Launching Data-Driven Playwright Demo with A11y Patching...")
    run_yaml_steps('actions.yaml', headless=False)
