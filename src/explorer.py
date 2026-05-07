import os
import asyncio
from typing import List, Dict, Any
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent

class Explorer:
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=SecretStr(api_key)
        )

    async def run_task(self, url: str, goal: str) -> List[Dict[str, Any]]:
        # Initialize browser and agent
        agent = Agent(
            task=f"Go to {url} and then {goal}",
            llm=self.llm,
        )
        
        history = await agent.run()
        return self._map_to_legacy(history.history)

    def _map_to_legacy(self, history: List[Any]) -> List[Dict[str, Any]]:
        legacy_history = []
        for step in history:
            # browser-use step has browser_action which contains the action data
            if not hasattr(step, 'browser_action') or step.browser_action is None:
                continue
            
            action_data = step.browser_action.dict()
            
            # Extract the action name and parameters
            # The dict usually looks like {'open_url': {'url': '...'}, 'click_element': {'index': 0}, ...}
            action_name = next(iter(action_data))
            params = action_data[action_name]
            
            legacy_step = None
            if action_name == "open_url":
                legacy_step = {
                    "action": "goto",
                    "url": params.get("url"),
                    "success": True
                }
            elif action_name == "click_element":
                legacy_step = {
                    "action": "click",
                    "text": params.get("index"),
                    "success": True
                }
            elif action_name == "input_text":
                legacy_step = {
                    "action": "fill",
                    "label": params.get("index"),
                    "value": params.get("text"),
                    "success": True
                }
            
            if legacy_step:
                legacy_history.append(legacy_step)
        
        return legacy_history
