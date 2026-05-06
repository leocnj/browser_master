from bs4 import BeautifulSoup

class Hardener:
    def filter_history(self, logs):
        """Returns only successful steps from the history."""
        if not logs:
            return []
        # Support both 'success' (bool) and 'status' (string) if LaVague changes its format
        return [step for step in logs if step.get("success") is True or step.get("status") == "success"]

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
            else:
                new_step["label"] = label
            
            # Remove brittle locator if we successfully mapped to semantic
            if "xpath" in new_step:
                del new_step["xpath"]
            if "css" in new_step:
                del new_step["css"]
                
        return new_step
