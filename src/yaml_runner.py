import yaml
import os
import jinja2
import asyncio
from playwright.async_api import async_playwright, expect

class YAMLRunner:
    def __init__(self, headless=True, slow_mo=1000):
        self.headless = headless
        self.slow_mo = slow_mo
        self.jinja_env = jinja2.Environment()
        
        # Load the scripts
        self.axe_path = os.path.join(os.path.dirname(__file__), 'axe.min.js')
        self.patch_path = os.path.join(os.path.dirname(__file__), 'a11y_patch.js')
        
        if not os.path.exists(self.axe_path):
            raise FileNotFoundError(f"Axe script not found at {self.axe_path}")
        if not os.path.exists(self.patch_path):
            raise FileNotFoundError(f"Patch script not found at {self.patch_path}")
            
        with open(self.axe_path, 'r') as f:
            self.axe_script = f.read()
        with open(self.patch_path, 'r') as f:
            self.patch_script = f.read()

    def _render_step(self, step, parameters):
        """Renders Jinja2 templates in step values."""
        if not parameters:
            return step
            
        new_step = {}
        for k, v in step.items():
            if isinstance(v, str) and "{{" in v:
                template = self.jinja_env.from_string(v)
                new_step[k] = template.render(**parameters)
            else:
                new_step[k] = v
        return new_step

    async def _execute_step(self, page, step):
        """Executes a single rendered step."""
        action = step.get('action')
        
        if action == 'goto':
            print(f"-> Navigating to {step['url']}")
            await page.goto(step['url'])
        
        elif action == 'fill':
            print(f"-> Filling '{step.get('label') or step.get('xpath')}' with '{step['value']}'")
            if 'label' in step:
                locator = page.get_by_label(step['label'])
            elif 'xpath' in step:
                locator = page.locator(f"xpath={step['xpath']}")
            else:
                raise ValueError("No locator found for fill action")
                
            try:
                await locator.fill(str(step['value']))
            except Exception as e:
                if "strict mode violation" in str(e):
                    await locator.first.fill(str(step['value']))
                else:
                    raise e
        
        elif action == 'select':
            print(f"-> Selecting '{step.get('label') or step.get('xpath')}' option '{step['value']}'")
            if 'label' in step:
                locator = page.get_by_label(step['label'])
            elif 'xpath' in step:
                locator = page.locator(f"xpath={step['xpath']}")
            else:
                raise ValueError("No locator found for select action")

            try:
                await locator.select_option(str(step['value']))
            except Exception as e:
                if "strict mode violation" in str(e):
                    await locator.first.select_option(str(step['value']))
                else:
                    raise e
        
        elif action == 'click':
            if 'label' in step:
                print(f"-> Clicking label '{step['label']}'")
                locator = page.get_by_label(step['label'])
            elif 'text' in step:
                print(f"-> Clicking text '{step['text']}'")
                locator = page.get_by_text(step['text'])
            elif 'xpath' in step:
                print(f"-> Clicking xpath '{step['xpath']}'")
                locator = page.locator(f"xpath={step['xpath']}")
            else:
                raise ValueError("No locator found for click action")
            
            try:
                await locator.click()
            except Exception as e:
                if "strict mode violation" in str(e):
                    await locator.first.click()
                elif "Timeout" in str(e) and ('text' in step or 'label' in step) and 'xpath' in step:
                    print(f"  ! Semantic locator failed, falling back to XPath: {step['xpath']}")
                    await page.locator(f"xpath={step['xpath']}").first.click()
                else:
                    raise e
        
        elif action == 'wait':
            ms = step.get('ms', 2000)
            print(f"-> Waiting {ms}ms")
            await page.wait_for_timeout(ms)
            
        elif action == 'verify':
            v_type = step.get('type', 'text')
            if v_type == 'url':
                print(f"-> Verifying URL matches '{step['value']}'")
                await expect(page).to_have_url(step['value'])
            else:
                val = step.get('value') or step.get('text')
                print(f"-> Verifying text '{val}' is visible")
                locator = page.get_by_text(val)
                try:
                    await expect(locator).to_be_visible()
                except Exception as e:
                    if "strict mode violation" in str(e):
                        await expect(locator.first).to_be_visible()
                    else:
                        raise e
        else:
            raise ValueError(f"Unknown action: {action}")

    async def run(self, yaml_path, parameters=None):
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found at {yaml_path}")

        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Merge provided parameters with defaults from YAML
        merged_params = {}
        for p in config.get('parameters', []):
            merged_params[p['name']] = p.get('default')
        if parameters:
            merged_params.update(parameters)

        print(f"--- Starting Enhanced YAML Engine ({yaml_path}) ---")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = await browser.new_context()
            
            # Inject both: Axe-core first, then our Smart Patcher
            await context.add_init_script(self.axe_script)
            await context.add_init_script(self.patch_script)
            
            page = await context.new_page()
            
            try:
                for raw_step in config.get('steps', []):
                    step = self._render_step(raw_step, merged_params)
                    await self._execute_step(page, step)
                
                print("--- Execution Successful ---")
                return True
            
            except Exception as e:
                print(f"❌ Error during execution: {e}")
                return False
            finally:
                await browser.close()

if __name__ == "__main__":
    import sys
    async def main():
        runner = YAMLRunner(headless=False)
        path = sys.argv[1] if len(sys.argv) > 1 else 'actions.yaml'
        await runner.run(path)
    
    asyncio.run(main())
