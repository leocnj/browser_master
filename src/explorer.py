from lavague.contexts.gemini import GeminiContext
from lavague.drivers.selenium import SeleniumDriver
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from llama_index.llms.gemini import Gemini
from llama_index.multi_modal_llms.gemini import GeminiMultiModal
from unittest.mock import patch
import os

class Explorer:
    def __init__(self, model_name="models/gemini-2.5-flash"):
        # Patch the allowed model lists in llama-index to bypass hardcoded validation
        # as gemini-1.5 is deprecated for this key.
        mm_patch_path = "llama_index.multi_modal_llms.gemini.base.GEMINI_MM_MODELS"
        llm_patch_path = "llama_index.llms.gemini.base.GEMINI_MODELS"
        
        with patch(mm_patch_path, (model_name, "models/gemini-1.5-flash-latest")):
            with patch(llm_patch_path, (model_name, "models/gemini-1.5-flash-latest")):
                # Ensure API key is passed correctly to sub-components
                api_key = os.getenv("GOOGLE_API_KEY")
                llm = Gemini(model_name=model_name, api_key=api_key)
                mm_llm = GeminiMultiModal(model_name=model_name, api_key=api_key)
                # GeminiContext expects model NAMES (strings) or it fails with concatenation error
                # if we pass the already initialized objects. 
                # HOWEVER, GeminiContext internally re-initializes them.
                # To bypass validation, we must patch during GeminiContext's init.
                self.context = GeminiContext(llm=model_name, mm_llm=model_name)

    def run_task(self, url: str, goal: str):
        # Initialize headless driver and components
        driver = SeleniumDriver(headless=True)
        try:
            action_engine = ActionEngine.from_context(self.context, driver)
            world_model = WorldModel.from_context(self.context)
            agent = WebAgent(world_model, action_engine)
            
            # Execute task
            agent.get(url)
            agent.run(goal)
            
            # Capture history
            history = agent.logger.logs
            return history
        finally:
            driver.driver.quit()
