from lavague.contexts.gemini import GeminiContext

class Explorer:
    def __init__(self, model_name="models/gemini-1.5-flash"):
        self.context = GeminiContext(llm=model_name)
