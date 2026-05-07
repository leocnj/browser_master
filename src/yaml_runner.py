import yaml
import os
import jinja2
from playwright.sync_api import sync_playwright, expect

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

    def _execute_step(self, page, step):
        """Executes a single rendered step."""
        action = step.get('action')
        
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
            
        elif action == 'verify':
            v_type = step.get('type', 'text')
            if v_type == 'url':
                print(f"-> Verifying URL matches '{step['value']}'")
                expect(page).to_have_url(step['value'])
            else:
                val = step.get('value') or step.get('text')
                print(f"-> Verifying text '{val}' is visible")
                expect(page.get_by_text(val)).to_be_visible()
        else:
            raise ValueError(f"Unknown action: {action}")

    def run(self, yaml_path, parameters=None):
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
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = browser.new_context()
            
            # Inject both: Axe-core first, then our Smart Patcher
            context.add_init_script(self.axe_script)
            context.add_init_script(self.patch_script)
            
            page = context.new_page()
            
            try:
                for raw_step in config.get('steps', []):
                    step = self._render_step(raw_step, merged_params)
                    self._execute_step(page, step)
                
                print("--- Execution Successful ---")
                return True
            
            except Exception as e:
                print(f"❌ Error during execution: {e}")
                return False
            finally:
                browser.close()

if __name__ == "__main__":
    import sys
    runner = YAMLRunner(headless=False)
    path = sys.argv[1] if len(sys.argv) > 1 else 'actions.yaml'
    runner.run(path)
