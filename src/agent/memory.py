from src.prompts.system_prompts import SYSTEM_PROMPT, get_long_conversation_reminder
from src.utils.config import MAX_HISTORY_TURNS, DRIFT_REMINDER_INTERVAL


class ConversationMemory:
    def __init__(self):
        self.turn_count = 0  # Track assistant turns for drift prevention
        self.reset()

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.turn_count = 0

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self.turn_count += 1

    def get_context_for_generation(self) -> list:
        """
        Build context with persona drift prevention.
        Every DRIFT_REMINDER_INTERVAL turns, injects a system reminder
        to keep Nova in character during long conversations.
        Adapted from Claude's <long_conversation_reminder> system.
        """
        # Keep System Prompt + Most Recent Turns
        if len(self.messages) > MAX_HISTORY_TURNS:
            context = [self.messages[0]] + self.messages[-(MAX_HISTORY_TURNS - 1):]
        else:
            context = list(self.messages)

        # Inject persona drift reminder every N assistant turns
        if self.turn_count > 0 and self.turn_count % DRIFT_REMINDER_INTERVAL == 0:
            reminder = {"role": "system", "content": get_long_conversation_reminder()}
            # Insert reminder just before the latest user message
            context.insert(-1, reminder)

        return context