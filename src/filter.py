def filter_history(history):
    return [step for step in history if step.get("success", False)]
