import os
import json
from playwright.sync_api import sync_playwright

def run_audit():
    """
    Injects axe-core into the mock Angular app and performs an accessibility audit.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("--- Navigating to http://localhost:4200 ---")
        page.goto("http://localhost:4200")
        
        # Search for an employee to bring up the "Hostile" section of the UI
        print("Searching for Employee ID 123 to reveal benefits section...")
        page.get_by_label("Employee ID Lookup").fill("123")
        page.get_by_text("Search Profile").click()
        page.wait_for_timeout(2000) # Give Angular time to render the benefits
        
        # Inject axe-core from our local file
        axe_path = os.path.join(os.path.dirname(__file__), 'src', 'axe.min.js')
        if not os.path.exists(axe_path):
            print(f"Error: {axe_path} not found. Please run the curl command first.")
            return

        with open(axe_path, 'r') as f:
            axe_script = f.read()
        
        page.evaluate(axe_script)
        
        # Run the axe audit
        print("🚀 Running axe-core audit...")
        results = page.evaluate("async () => await axe.run()")
        
        violations = results.get('violations', [])
        
        if not violations:
            print("✅ No accessibility violations found!")
        else:
            print(f"\n❌ Found {len(violations)} Accessibility Violations:")
            
            for i, v in enumerate(violations, 1):
                print(f"\n{i}. [{v['impact'].upper()}] {v['help']}")
                print(f"   Description: {v['description']}")
                print(f"   Fix Guide: {v['helpUrl']}")
                
                # Show the first few offending HTML elements
                for node in v['nodes'][:3]: # Limit to 3 nodes per violation
                    print(f"   - Offending Element: {node['target']}")
                    print(f"     Why it failed: {node['failureSummary']}")
            
        browser.close()
        print("\n--- Audit Complete ---")

if __name__ == "__main__":
    run_audit()
