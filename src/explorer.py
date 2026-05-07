from lavague.contexts.gemini import GeminiContext
from lavague.drivers.selenium import SeleniumDriver
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from llama_index.llms.gemini import Gemini
from llama_index.multi_modal_llms.gemini import GeminiMultiModal
from unittest.mock import patch
import os
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

# Disable LaVague telemetry to prevent hangs on exit/timeout
os.environ["LAVAGUE_TELEMETRY"] = "NONE"

def patch_gemini_sdk():
    """
    Monkeypatches the Google Generative AI SDK to handle multi-part responses
    which are common in Gemini 2.5/2.0 but break the .text accessor used by llama-index.
    """
    def safe_text(self):
        try:
            # Concatenate all text parts from all candidates (usually just one candidate)
            parts = []
            for candidate in self.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        parts.append(part.text)
            return "".join(parts)
        except Exception:
            return ""

    # Apply global property patch
    GenerateContentResponse.text = property(safe_text)

# Apply SDK patch on import
patch_gemini_sdk()

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
                # GeminiContext internally re-initializes models, so we must 
                # provide strings and patch during its initialization.
                self.context = GeminiContext(llm=model_name, mm_llm=model_name, embedding="models/gemini-embedding-2")

    def run_task(self, url: str, goal: str):
        # Initialize headless driver and components
        driver = SeleniumDriver(headless=True)
        try:
            action_engine = ActionEngine.from_context(self.context, driver)
            world_model = WorldModel.from_context(self.context)
            agent = WebAgent(world_model, action_engine)
            
            # Execute task
            agent.get(url)
            try:
                agent.run(goal)
            except Exception as e:
                print(f"⚠️ Agent stopped early: {e}")
            
            # Capture history (including partial progress)
            history = agent.logger.logs
            return history
        finally:
            driver.driver.quit()
