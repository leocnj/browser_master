from bs4 import BeautifulSoup
import json
import re

class Hardener:
    def __init__(self, context=None):
        self.context = context

    def filter_history(self, logs):
        """Returns only successful, relevant steps from the history."""
        if not logs:
            return []
        
        relevant_actions = ["click", "fill", "select", "goto", "verify"]
        filtered = []
        for step in logs:
            action = step.get("action")
            success = step.get("success") is True or step.get("status") == "success"
            
            # Skip noise like scrolls or unknown actions
            if success and action in relevant_actions:
                filtered.append(step)
        return filtered

    def _find_label_in_html(self, html_snippet):
        """Heuristic to find a label for an element within a small HTML snippet."""
        if not html_snippet:
            return None
        soup = BeautifulSoup(html_snippet, 'html.parser')
        
        # Strategy 1: Explicit <label> tag
        label_tag = soup.find('label')
        if label_tag:
            return label_tag.get_text().strip().rstrip(":")
            
        # Strategy 2: Preceding sibling or parent text (heuristic)
        inputs = soup.find_all(['input', 'select', 'textarea', 'button'])
        for inp in inputs:
            prev = inp.find_previous_sibling()
            if prev and prev.get_text().strip():
                return prev.get_text().strip().rstrip(":")
            
            parent = inp.parent
            if parent and parent.contents:
                first = parent.contents[0]
                if hasattr(first, 'get_text') and first.get_text().strip():
                    return first.get_text().strip().rstrip(":")
                elif isinstance(first, str) and first.strip():
                    return first.strip().rstrip(":")
        return None

    def map_to_semantic(self, step):
        """Converts technical locators to semantic ones based on metadata."""
        new_step = step.copy()
        action = new_step.get("action")
        instruction = new_step.get("instruction", "")
        html = new_step.get("element_html", "")
        
        label = None
        
        # Try extracting from instruction first (often contains the user's intent)
        if instruction:
            if "Click " in instruction:
                label = instruction.replace("Click ", "").strip()
            elif "Fill " in instruction:
                # "Fill Employee ID with 123" -> "Employee ID"
                parts = instruction.replace("Fill ", "").split(" with ")
                if len(parts) > 0:
                    label = parts[0].strip()
        
        # Fallback to HTML heuristics if instruction extraction failed
        if not label and html:
            label = self._find_label_in_html(html)
            
        if label:
            # Clean up the label
            label = label.strip().rstrip(":")
            
            if action == "click":
                new_step["text"] = label
            elif action == "fill":
                new_step["label"] = label
            elif action == "select":
                new_step["label"] = label
            
            # Remove brittle locator if we successfully mapped to semantic
            if "xpath" in new_step:
                del new_step["xpath"]
            if "css" in new_step:
                del new_step["css"]
                
        return new_step

    def detect_verification(self, history):
        """Identifies and adds a verification step based on the end of the history."""
        if not history:
            return history
        
        last_step = history[-1]
        # Check URL change
        first_url = next((s.get("url") for s in history if s.get("url")), None)
        last_url = last_step.get("url")
        
        if last_url and first_url and last_url != first_url:
            history.append({
                "action": "verify",
                "type": "url",
                "value": last_url
            })
            return history

        # Check for success text in HTML or instruction
        success_keywords = ["success", "saved", "complete", "thank you", "confirmed", "updated"]
        html = last_step.get("element_html", "").lower()
        instruction = last_step.get("instruction", "").lower()
        
        for kw in success_keywords:
            if kw in html or kw in instruction:
                # Extract snippet
                value = kw.capitalize()
                if kw in html:
                    # Very basic snippet extraction
                    value = last_step.get("element_html")
                    if len(value) > 100:
                        value = value[:100] + "..."
                
                history.append({
                    "action": "verify",
                    "type": "text",
                    "value": value
                })
                break
        
        return history

    async def parameterize(self, goal, history):
        """Uses LLM to identify parameters and programmatically replaces them in history."""
        if not self.context or not self.context.llm:
            return {"parameters": [], "steps": history}

        # Clean history for prompt (minimal data)
        clean_history = []
        for i, step in enumerate(history):
            s = {k: v for k, v in step.items() if k in ["action", "label", "text", "value", "url"]}
            s["id"] = i
            clean_history.append(s)

        prompt = f"""Analyze the GOAL and the sequence of ACTIONS.
Identify values (like IDs, names, dates) in the ACTIONS that come from the GOAL.
Return a JSON object with:
- 'parameters': a list of {{'name': '...', 'default': '...', 'description': '...'}}
- 'mappings': a list of {{'step_id': int, 'field': '...', 'param_name': '...'}} 

GOAL: {goal}
ACTIONS: {json.dumps(clean_history, indent=2)}

JSON output only."""

        response = await self.context.llm.ainvoke(prompt)
        text = response.content
        
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                
                # Programmatically replace values to ensure no fields are lost
                new_steps = [s.copy() for s in history]
                for m in data.get('mappings', []):
                    idx = m['step_id']
                    field = m['field']
                    param = m['param_name']
                    if idx < len(new_steps) and field in new_steps[idx]:
                        new_steps[idx][field] = f"{{{{{param}}}}}"
                
                return {
                    "parameters": data.get('parameters', []),
                    "steps": new_steps
                }
            except Exception:
                pass
        
        return {"parameters": [], "steps": history}

    async def harden(self, goal, raw_logs):
        """Orchestrates the full hardening pipeline."""
        filtered = self.filter_history(raw_logs)
        # Ensure we have at least interaction metadata
        semantic = [self.map_to_semantic(s) for s in filtered]
        verified = self.detect_verification(semantic)
        parameterized = await self.parameterize(goal, verified)
        
        # Final cleanup: remove internal fields used by Hardener
        final_steps = []
        for step in parameterized["steps"]:
            clean_step = {k: v for k, v in step.items() if k in ["action", "label", "text", "value", "url", "type", "ms"]}
            # If action is missing but URL is present, default to 'goto'
            if not clean_step.get("action") and clean_step.get("url"):
                clean_step["action"] = "goto"
            
            if clean_step.get("action"):
                final_steps.append(clean_step)
        
        parameterized["steps"] = final_steps
        return parameterized
