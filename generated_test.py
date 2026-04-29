import playwright.sync_api
import time

def run(page: playwright.sync_api.Page, employee_id: str, benefit_type: str):
    print(f"Navigating to http://localhost:4200...")
    page.goto("http://localhost:4200")
    
    # Wait for the app to load
    page.wait_for_selector('.hostile-wrapper')
    
    print(f"Entering employee ID: {employee_id} (using fallback XPath locator)")
    page.locator("xpath=//span[text()='Emp ID:']/following-sibling::input").fill(employee_id)
    
    print("Clicking 'Find' (using get_by_text fallback)")
    page.get_by_text("Find").click()
    
    # Wait for backend response to render
    page.locator("xpath=//span[text()='Update Dental:']/following-sibling::input").wait_for(state="visible")
    
    print(f"Updating dental plan to: {benefit_type} (using fallback XPath locator)")
    page.locator("xpath=//span[text()='Update Dental:']/following-sibling::input").fill(benefit_type)
    
    print("Clicking 'Save Plan' (using get_by_text fallback)")
    page.get_by_text("Save Plan").click()
    
    # Wait a bit to observe the final state
    page.wait_for_timeout(2000)
    print("✅ Playwright script executed successfully!")

if __name__ == '__main__':
    with playwright.sync_api.sync_playwright() as p:
        # Running headless=False and adding slow_mo so you can visually watch the automation
        browser = p.chromium.launch(headless=False, slow_mo=1500)
        page = browser.new_page()

        employee_id_param = '123'
        benefit_type_param = 'Super Platinum Plan'

        try:
            run(page, employee_id=employee_id_param, benefit_type=benefit_type_param)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()