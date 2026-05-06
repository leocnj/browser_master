from lavague.contexts.gemini import GeminiContext
from lavague.drivers.selenium import SeleniumDriver
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent

class Explorer:
    def __init__(self, model_name="models/gemini-1.5-flash"):
        self.context = GeminiContext(llm=model_name)

    def run_task(self, url: str, goal: str):
        # Initialize headless driver and components
        driver = SeleniumDriver(headless=True)
        action_engine = ActionEngine.from_context(self.context, driver)
        world_model = WorldModel.from_context(self.context)
        agent = WebAgent(world_model, action_engine)
        
        # Execute task
        agent.get(url)
        agent.run(goal)
        
        # Capture history and cleanup
        history = agent.logger.logs
        driver.driver.quit()
        return history
