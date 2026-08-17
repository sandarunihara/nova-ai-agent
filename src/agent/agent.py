"""
src/agent/agent.py
Nova Agent with Context-Aware Search, Weather, Math Solver, Document RAG, and Response Sanitization.
"""

import re
from src.agent.memory import ConversationMemory
from src.models.llm_client import LLMClient
from src.tools.search import search_and_fetch_knowledge
from src.tools.weather import get_live_weather
from src.tools.math_solver import extract_and_solve_math
from src.tools.document_rag import DocumentStore
from src.prompts.system_prompts import (
    build_search_augmented_prompt,
    build_math_narrative_prompt,
    build_self_identity_prompt,
    build_user_identity_prompt,
    build_creator_prompt,
    build_greeting_prompt,
    build_document_rag_prompt,
)
from src.utils.config import (
    EMBEDDING_MODEL_ID, CACHE_DIR, DOC_CHUNK_SIZE,
    DOC_CHUNK_OVERLAP, DOC_SEARCH_TOP_K, DOC_RELEVANCE_THRESHOLD,
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
        self.doc_store = DocumentStore(
            embedding_model_id=EMBEDDING_MODEL_ID,
            chunk_size=DOC_CHUNK_SIZE,
            chunk_overlap=DOC_CHUNK_OVERLAP,
            cache_dir=CACHE_DIR,
        )

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

        # 0. Document Management Commands
        lower_input = user_input.lower().strip()

        if lower_input.startswith("load "):
            filepath = user_input[5:].strip()
            print(f"\n📄 [Nova Docs] Loading '{filepath}'...")
            result = self.doc_store.load_document(filepath)
            if result["success"]:
                print(f"📄 [Nova Docs] Extracted {result['pages']} page(s), {result['chunks']} chunks indexed.")
                print(f"📄 [Nova Docs] Document '{result['doc_name']}' is now loaded and searchable.")
            else:
                print(f"❌ [Nova Docs] {result['error']}")
            return ""

        if lower_input == "docs":
            docs = self.doc_store.list_documents()
            if not docs:
                print("\n📄 No documents loaded. Use 'load <filepath>' to add one.")
            else:
                print("\n📄 Loaded Documents:")
                for i, d in enumerate(docs, 1):
                    print(f"  {i}. {d['name']} — {d['pages']} page(s), {d['chunks']} chunks")
            return ""

        if lower_input.startswith("unload "):
            doc_name = user_input[7:].strip()
            result = self.doc_store.unload_document(doc_name)
            if result["success"]:
                print(f"\n📄 [Nova Docs] Removed '{result['doc_name']}' ({result['chunks_removed']} chunks cleared).")
            else:
                print(f"\n❌ [Nova Docs] {result['error']}")
            return ""

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

        # 4. Document RAG — Search loaded documents for relevant context
        elif self.doc_store.has_documents and (doc_result := self._try_document_search(user_input)):
            doc_context, source_info, best_score = doc_result
            print(f"📄 [Nova Docs] Searching loaded documents... (best match: {best_score:.2f} similarity)")
            augmented = build_document_rag_prompt(user_input, doc_context, source_info)
            is_rag = True

        # 5. Math Solver Engine (Secure Python AST Execution + Narrative Synthesis)
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

        # 6. General Search Planning & Web Retrieval
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

    def _try_document_search(self, query: str) -> tuple[str, str, float] | None:
        """
        Search loaded documents for content relevant to the query.
        Returns (doc_context, source_info, best_score) if relevant content found,
        or None if no relevant content.
        """
        results = self.doc_store.search(query, top_k=DOC_SEARCH_TOP_K)

        if not results:
            return None

        best_score = results[0][1]

        if best_score < DOC_RELEVANCE_THRESHOLD:
            return None

        # Build context from top chunks
        context_parts = []
        source_docs = set()
        for chunk, score in results:
            if score >= DOC_RELEVANCE_THRESHOLD * 0.7:  # Include slightly below threshold too
                context_parts.append(
                    f"[Source: {chunk.doc_name}, Page {chunk.page_num}]\n{chunk.text}"
                )
                source_docs.add(chunk.doc_name)

        doc_context = "\n\n---\n\n".join(context_parts)
        source_info = ", ".join(sorted(source_docs))

        return doc_context, source_info, best_score