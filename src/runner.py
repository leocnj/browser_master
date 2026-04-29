import os
import asyncio
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ConfigDict

class MyChatGoogle(ChatGoogleGenerativeAI):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True, populate_by_name=True)
    provider: str = "google"
    
    @property
    def model_name(self):
        return self.model

async def run_explorer(task: str):
    llm = MyChatGoogle(model="gemini-2.5-flash")
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    return history
