import os
import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI
from pydantic import ConfigDict

class MyChatOpenAI(ChatOpenAI):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True, populate_by_name=True)
    provider: str = "openai"
    
    @property
    def model(self):
        return self.model_name

async def run_explorer(task: str):
    llm = MyChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        model="openai/gpt-4o-2024-11-20"
    )
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    return history
