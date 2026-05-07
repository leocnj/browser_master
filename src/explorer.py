import os
import asyncio
from typing import List, Dict, Any
from pydantic import SecretStr
from browser_use import Agent, ChatGoogle

class Explorer:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        self.llm = ChatGoogle(
            model=model_name,
            api_key=api_key
        )

    async def run_task(self, url: str, goal: str) -> List[Dict[str, Any]]:
        # Initialize agent
        agent = Agent(
            task=f"Go to {url} and then {goal}",
            llm=self.llm,
        )
        
        history = await agent.run()
        return self._map_to_legacy(history.history)

    def _map_to_legacy(self, history: List[Any]) -> List[Dict[str, Any]]:
        legacy_history = []
        for step in history:
            # step is AgentHistory
            if not step.model_output or not step.model_output.action:
                continue
            
            # Context for hardener
            instruction = step.model_output.thinking or ""
            if step.model_output.next_goal:
                instruction += f" Next goal: {step.model_output.next_goal}"
            
            for i, action_model in enumerate(step.model_output.action):
                # action_model.root is the specific action wrapper (e.g. ClickActionModel)
                wrapper = action_model.root
                
                legacy_step = {
                    "success": True, 
                    "instruction": instruction,
                    "url": step.state.url if step.state else None
                }
                
                # Extract metadata from interacted element if available
                if step.state and step.state.interacted_element:
                    # Usually one action per step in standard runs, but handle multiple
                    if i < len(step.state.interacted_element):
                        el = step.state.interacted_element[i]
                        if el:
                            legacy_step["element_text"] = el.ax_name
                            legacy_step["xpath"] = el.x_path
                            # Construct a pseudo-HTML snippet for the Hardener's heuristic
                            attrs = " ".join([f'{k}="{v}"' for k, v in el.attributes.items()])
                            legacy_step["element_html"] = f'<{el.node_name} {attrs}>{el.ax_name}</{el.node_name}>'

                # Check for standard browser-use tools and map to legacy actions
                if hasattr(wrapper, 'navigate'):
                    legacy_step.update({
                        "action": "goto",
                        "url": wrapper.navigate.url
                    })
                elif hasattr(wrapper, 'click'):
                    legacy_step.update({
                        "action": "click",
                        "text": legacy_step.get("element_text") or wrapper.click.index
                    })
                elif hasattr(wrapper, 'input'):
                    legacy_step.update({
                        "action": "fill",
                        "label": legacy_step.get("element_text") or wrapper.input.index,
                        "value": wrapper.input.text
                    })
                elif hasattr(wrapper, 'click_element'):
                    legacy_step.update({
                        "action": "click",
                        "text": legacy_step.get("element_text") or wrapper.click_element.index
                    })
                elif hasattr(wrapper, 'input_text'):
                    legacy_step.update({
                        "action": "fill",
                        "label": legacy_step.get("element_text") or wrapper.input_text.index,
                        "value": wrapper.input_text.text
                    })
                elif hasattr(wrapper, 'open_url'):
                    legacy_step.update({
                        "action": "goto",
                        "url": wrapper.open_url.url
                    })
                
                if "action" in legacy_step:
                    legacy_history.append(legacy_step)
        
        return legacy_history
