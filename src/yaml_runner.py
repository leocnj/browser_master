import yaml
import os
from playwright.sync_api import sync_playwright

def run_yaml_steps(yaml_path: str, headless: bool = False):
    """
    Parses a YAML action sequence and executes it using Playwright.
    Automatically injects a JS A11y patch to fix hostile DOMs.
    """
    if not os.path.exists(yaml_path):
        print(f"Error: YAML file not found at {yaml_path}")
        return

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Load the a11y patch script
    patch_path = os.path.join(os.path.dirname(__file__), 'a11y_patch.js')
    with open(patch_path, 'r') as f:
        patch_script = f.read()

    print(f"--- Starting YAML Playwright Engine ({yaml_path}) ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=1500)
        context = browser.new_context()
        
        # KEY: Inject the a11y patch so it runs before any other script
        context.add_init_script(patch_script)
        
        page = context.new_page()
        
        for step in config.get('steps', []):
            action = step.get('action')
            
            try:
                if action == 'goto':
                    print(f"-> Navigating to {step['url']}")
                    page.goto(step['url'])
                
                elif action == 'fill':
                    print(f"-> Filling label '{step['label']}' with '{step['value']}'")
                    page.get_by_label(step['label']).fill(step['value'])
                
                elif action == 'select':
                    print(f"-> Selecting label '{step['label']}' option '{step['value']}'")
                    page.get_by_label(step['label']).select_option(step['value'])
                
                elif action == 'click':
                    if 'label' in step:
                        print(f"-> Clicking label '{step['label']}'")
                        page.get_by_label(step['label']).click()
                    else:
                        print(f"-> Clicking text '{step['text']}'")
                        page.get_by_text(step['text']).click()
                
                elif action == 'wait':
                    ms = step.get('ms', 2000)
                    print(f"-> Waiting {ms}ms")
                    page.wait_for_timeout(ms)
            
            except Exception as e:
                print(f"❌ Error during step {step}: {e}")
                # Take a screenshot on failure if needed
                break
        
        print("--- Execution Complete ---")
        browser.close()

if __name__ == "__main__":
    run_yaml_steps('actions.yaml', headless=False)
