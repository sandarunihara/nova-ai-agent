from src.prompts.system_prompts import SYSTEM_PROMPT
from src.utils.config import MAX_HISTORY_TURNS

class ConversationMemory:
    def __init__(self):
        self.reset()

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def get_context_for_generation(self) -> list:
        # Keep System Prompt + Most Recent Turns
        if len(self.messages) > MAX_HISTORY_TURNS:
            return [self.messages[0]] + self.messages[-(MAX_HISTORY_TURNS - 1):]
        return self.messages