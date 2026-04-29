import playwright.sync_api
import time

def run(page: playwright.sync_api.Page, employee_id: str, medical_coverage: str):
    print(f"Navigating to http://localhost:4200...")
    page.goto("http://localhost:4200")
    
    # Wait for the app to load
    page.wait_for_selector('.glass-panel')
    
    print(f"Entering employee ID: {employee_id} (using semantic locator)")
    # Using the semantic label fallback
    page.get_by_label("Employee ID Lookup").fill(employee_id)
    
    print("Clicking 'Search Profile' (using get_by_text fallback)")
    page.get_by_text("Search Profile").click()
    
    # Wait for backend response to render the benefits section
    page.locator("xpath=//span[text()='Medical Coverage:']/following-sibling::select").wait_for(state="visible")
    
    print(f"Updating Medical Coverage to: {medical_coverage} (using hostile DOM XPath fallback)")
    # Using the XPath fallback because the select has no label, id, or name
    page.locator("xpath=//span[text()='Medical Coverage:']/following-sibling::select").select_option(medical_coverage)
    
    print("Clicking 'Submit Updates' (using hostile DOM get_by_text fallback on a div)")
    page.get_by_text("Submit Updates").click()
    
    # Wait a bit to observe the final state
    page.wait_for_timeout(2000)
    print("✅ Playwright script executed successfully!")

if __name__ == '__main__':
    with playwright.sync_api.sync_playwright() as p:
        # Running headless=False and adding slow_mo so you can visually watch the automation
        browser = p.chromium.launch(headless=False, slow_mo=1500)
        page = browser.new_page()

        employee_id_param = '123'
        medical_coverage_param = 'Platinum Medical'

        try:
            run(page, employee_id=employee_id_param, medical_coverage=medical_coverage_param)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()