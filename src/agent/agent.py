"""
src/agent/agent.py
Nova Agent with Context-Aware Search, Dedicated Weather Tool, Safe Math Solver, and Response Sanitization.
"""

import re
from src.agent.memory import ConversationMemory
from src.models.llm_client import LLMClient
from src.tools.search import search_and_fetch_knowledge
from src.tools.weather import get_live_weather
from src.tools.math_solver import extract_and_solve_math
from src.prompts.system_prompts import (
    build_search_augmented_prompt,
    build_math_narrative_prompt,
    build_self_identity_prompt,
    build_user_identity_prompt,
    build_creator_prompt,
    build_greeting_prompt,
)

_FILLER_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^thank you.*",
        r"^if you (encounter|have|need|require).*",
        r"^(should|shall) there be.*",
        r"^we look forward.*",
        r"^let us embark.*",
        r"^feel free to.*",
        r"^don'?t hesitate to.*",
        r"^(please )?let me know if (you need|there('s| is)|you have).*",
        r"^(i('m| am) )?happy to (help|assist).*",
        r"^best regards.*",
        r"^- ?NOVA$",
        r"^NOVA$",
    ]
]

_WEATHER_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"\b(weather|temperature|temp|forecast|rain|humidity|climate)\b",
    ]
]


# Fast-path regex: queries containing digits + math-like context are candidates for LLM classification
_MATH_CANDIDATE_PATTERN = re.compile(
    r'(?:'
    r'\d+\s*[%$°]|'           
    r'\d+.*\d+|'               
    r'angle|height|area|volume|radius|diameter|perimeter|'
    r'how many|how long|how far|how much|how fast|'
    r'what is the .*(total|sum|product|difference|result|value|answer|height|distance|speed|rate|cost|price|amount)|'
    r'find the|solve|calculate|compute|evaluate|determine|'
    r'probability|chance|odds|'
    r'invested|interest|compound|'
    r'equation|formula|'
    r'factorial|permutation|combination|'
    r'triangle|circle|rectangle|square|cylinder|sphere|'
    r'sin|cos|tan|sqrt|log|'
    r'rate|speed|velocity|acceleration|'
    r'pipe|tank|fill|empty|drain|'
    r'ladder|wall|feet|meters'
    r')', re.IGNORECASE
)

_USER_IDENTITY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [r"\bwho am i\b", r"\bmy name\b"]]
_CREATOR_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [r"\byour (creator|owner|master)\b", r"\bwho (created|made|built|owns) you\b", r"\bcreated you\b"]]
_SELF_IDENTITY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [r"\bwho are you\b", r"\bwhat is your name\b", r"\bintroduce yourself\b", r"\byour purpose\b"]]


class NovaAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.memory = ConversationMemory()
        self.last_topic = ""

    @staticmethod
    def classify_identity_query(query: str):
        if any(p.search(query) for p in _USER_IDENTITY_PATTERNS):
            return "user"
        if any(p.search(query) for p in _CREATOR_PATTERNS):
            return "creator"
        if any(p.search(query) for p in _SELF_IDENTITY_PATTERNS):
            return "self"
        return None

    @staticmethod
    def is_greeting(query: str) -> bool:
        clean = query.lower().strip().rstrip("!?.")
        return clean in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hi nova", "hello nova"]

    @staticmethod
    def is_weather_query(query: str) -> bool:
        return any(p.search(query) for p in _WEATHER_PATTERNS)

    def is_math_query(self, query: str) -> bool:
        """Uses a fast-path regex pre-check + LLM classifier to detect math problems."""
        # Exclude queries clearly about identity, weather, or general knowledge
        lower = query.lower()
        if any(w in lower for w in ["president", "who is", "weather", "capital of", "explain", "tell me about", "write a", "create a"]):
            return False

        # Fast-path: if the query doesn't look like it could be math, skip LLM call
        if not _MATH_CANDIDATE_PATTERN.search(query):
            return False

        # Use LLM classifier for the final decision
        print("🔍 [Nova Engine] Classifying query intent...")
        return self.llm.classify_math_query(query)

    @staticmethod
    def _clean_response(text: str) -> str:
        # Hard purge of any placeholder bracket text like [Insert ...] or [Unit]
        text = re.sub(r'\[Insert [^\]]+\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[Unit\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?\]', '', text)  # remove leftover square bracket markers

        lines = text.rstrip().split("\n")
        while lines:
            candidate = lines[-1].strip()
            if not candidate:
                lines.pop()
                continue
            if any(p.match(candidate) for p in _FILLER_PATTERNS):
                lines.pop()
                continue
            break
        return "\n".join(lines).rstrip()

    def process_turn(self, user_input: str) -> str:
        is_rag = False

        # 1. Greeting Check
        if self.is_greeting(user_input):
            print("👋 [Nova Engine] Greeting detected — responding with respect...")
            augmented = build_greeting_prompt(user_input)

        # 2. Identity Check
        elif self.classify_identity_query(user_input):
            identity_type = self.classify_identity_query(user_input)
            if identity_type == "user":
                print("🧠 [Nova Engine] User identity query...")
                augmented = build_user_identity_prompt(user_input)
            elif identity_type == "creator":
                print("🧠 [Nova Engine] Creator query...")
                augmented = build_creator_prompt(user_input)
            elif identity_type == "self":
                print("🧠 [Nova Engine] Self-identity query...")
                augmented = build_self_identity_prompt(user_input)

        # 3. Dedicated Live Weather Check (Fast & Reliable)
        elif self.is_weather_query(user_input):
            print(f"🌤️ [Nova Weather Engine] Fetching real-time meteorological data for: '{user_input}'...")
            weather_data = get_live_weather(user_input)
            if weather_data:
                augmented = build_search_augmented_prompt(user_input, weather_data)
                is_rag = True
            else:
                augmented = user_input

        # 4. Math Solver Engine (Secure Python AST Execution + Narrative Synthesis)
        elif self.is_math_query(user_input):
            print(f"🧮 [Nova Math Engine] Computing precise math expression...")
            expr, exact_val = extract_and_solve_math(user_input, self.llm)
            
            if exact_val is not None:
                print(f"🧮 [Nova Math Engine] Expression: {expr} | Exact Result: {exact_val}")
                augmented = build_math_narrative_prompt(user_input, expr, exact_val)
                is_rag = True
            else:
                print("⚠️ [Nova Math Engine] Math extraction fallback to internal reasoning.")
                augmented = user_input

        # 5. General Search Planning & Web Retrieval
        else:
            search_query = self.llm.plan_search_query(user_input, recent_context=self.last_topic)

            if search_query.upper() != "NONE" and len(search_query) > 2:
                print(f"🔍 [Nova Engine] Query: '{search_query}'...")
                web_context = search_and_fetch_knowledge(search_query)

                if web_context:
                    augmented = build_search_augmented_prompt(user_input, web_context)
                    is_rag = True
                    self.last_topic = user_input
                else:
                    augmented = user_input
            else:
                print("🧠 [Nova Engine] Using internal reasoning & code intelligence...")
                augmented = user_input

        # Generation
        self.memory.add_user_message(augmented)
        context = self.memory.get_context_for_generation()

        if self.memory.turn_count > 0 and self.memory.turn_count % 4 == 0:
            print("🔒 [Nova Engine] Persona stability reminder injected.")

        print("\nNova: ", end="", flush=True)
        raw_response = self.llm.generate(context, is_factual_rag=is_rag)
        response = self._clean_response(raw_response)

        # Update clean conversation memory
        self.memory.messages.pop()
        self.memory.add_user_message(user_input)
        self.memory.add_assistant_message(response)

        return response