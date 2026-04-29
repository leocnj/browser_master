import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI

async def run_explorer(task: str):
    llm = ChatOpenAI(model="gpt-4o")
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    return history
