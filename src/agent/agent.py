import re
from src.agent.memory import ConversationMemory
from src.models.llm_client import LLMClient
from src.tools.search import search_duckduckgo
from src.prompts.system_prompts import build_search_augmented_prompt, build_identity_prompt

class NovaAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.memory = ConversationMemory()

    def is_identity_query(self, query: str) -> bool:
        patterns = [
            r"\bwho are you\b", r"\bwho am i\b", r"\bcreator\b", 
            r"\bwho created\b", r"\bwhat is your name\b", r"\bwhat do you do\b",
            r"\bintroduce yourself\b"
        ]
        return any(re.search(p, query.lower()) for p in patterns)

    def process_turn(self, user_input: str) -> str:
        is_rag = False

        # 1. Identity Check
        if self.is_identity_query(user_input):
            print("🧠 [Nova Engine] Identity core active...")
            augmented = build_identity_prompt(user_input)

        # 2. Dynamic Tool Calling / Planning
        else:
            search_query = self.llm.plan_search_query(user_input)

            if search_query.upper() != "NONE" and len(search_query) > 2:
                print(f"🔍 [Dynamic Search] Model formulated query: '{search_query}'...")
                web_context = search_duckduckgo(search_query)
                
                if web_context:
                    augmented = build_search_augmented_prompt(user_input, web_context)
                    is_rag = True
                else:
                    print("⚠️ [Search Returned No Results] Falling back to internal reasoning.")
                    augmented = user_input
            else:
                print("🧠 [Nova Engine] Decision='NONE' | Using internal reasoning & code intelligence...")
                augmented = user_input

        # 3. Context Formulation and Generation
        self.memory.add_user_message(augmented)
        context = self.memory.get_context_for_generation()
        
        print("\nNova: ", end="", flush=True)
        response = self.llm.generate(context, is_factual_rag=is_rag)
        
        # 4. Store clean dialogue in memory
        self.memory.messages.pop()
        self.memory.add_user_message(user_input)
        self.memory.add_assistant_message(response)
        
        return response