"""
generate_project_guide.py
Generates a comprehensive PDF guide for the NOVA AI Agent project.
Explains every file, every line, architecture, and data flow.
Requires: fpdf2  (pip install fpdf2)
"""

from fpdf import FPDF
import textwrap, os

class ProjectGuidePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        # Use built-in fonts only (no external TTF needed)

    def chapter_title(self, title, level=1):
        if level == 1:
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(10, 60, 130)
            self.cell(0, 14, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(10, 60, 130)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)
        elif level == 2:
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(30, 90, 160)
            self.cell(0, 11, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(3)
        elif level == 3:
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(50, 110, 180)
            self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def code_block(self, code, highlight_color=(245, 245, 255)):
        self.set_fill_color(*highlight_color)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(20, 20, 80)
        for line in code.split("\n"):
            safe_line = line.replace("\t", "    ")
            # Wrap long lines
            if len(safe_line) > 105:
                wrapped = textwrap.wrap(safe_line, width=105)
                for w in wrapped:
                    self.cell(0, 4.5, "  " + w, new_x="LMARGIN", new_y="NEXT", fill=True)
            else:
                self.cell(0, 4.5, "  " + safe_line, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def explanation(self, text):
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def line_explain(self, line_num, code_line, explain_text):
        """Print a line number, the code, and its explanation."""
        # Code line
        self.set_fill_color(245, 245, 255)
        self.set_font("Courier", "B", 8.5)
        self.set_text_color(120, 40, 40)
        label = f"Line {line_num}: "
        self.set_font("Courier", "", 8.5)
        self.set_text_color(20, 20, 80)
        safe = code_line.replace("\t", "    ")
        if len(safe) > 100:
            safe = safe[:97] + "..."
        self.cell(0, 4.5, f"  {label}{safe}", new_x="LMARGIN", new_y="NEXT", fill=True)
        # Explanation
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 4.8, f"    -> {explain_text}")
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(6, 5.5, chr(8226))
        self.multi_cell(0, 5.5, text)

    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, "NOVA AI Agent Project - Complete Line-by-Line Guide", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def build_pdf():
    pdf = ProjectGuidePDF()
    pdf.alias_nb_pages()

    # =====================================================================
    # COVER PAGE
    # =====================================================================
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(10, 60, 130)
    pdf.cell(0, 15, "NOVA AI Agent Project", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "Complete Line-by-Line Code Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "A Personal AI Assistant with Web Search, Math Solving,", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "Document RAG, Weather, and Conversation Memory", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Created for: Sandaru Nihara", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Model: Qwen 2.5 1.5B Instruct (4-bit Quantized)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Framework: HuggingFace Transformers + PyTorch", align="C", new_x="LMARGIN", new_y="NEXT")

    # =====================================================================
    # TABLE OF CONTENTS
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("Table of Contents")
    toc_items = [
        "1. Project Overview & Architecture",
        "2. Directory Structure",
        "3. File: src/utils/config.py - Configuration & Hyperparameters",
        "4. File: src/prompts/system_prompts.py - System Prompts & Prompt Engineering",
        "5. File: src/agent/memory.py - Conversation Memory System",
        "6. File: src/models/llm_client.py - LLM Client (Model Loading & Generation)",
        "7. File: src/tools/search.py - Web Search & Knowledge Extraction",
        "8. File: src/tools/weather.py - Live Weather Tool",
        "9. File: src/tools/math_solver.py - Safe Math Expression Evaluator",
        "10. File: src/tools/document_rag.py - Document RAG Engine",
        "11. File: src/agent/agent.py - The Core Agent (Orchestrator)",
        "12. File: main.py - Application Entry Point",
        "13. File: tests/test_math_solver.py - Unit Tests",
        "14. File: tests/sample_doc.md - Sample Test Document",
        "15. Complete Data Flow Walkthrough",
        "16. Key Design Decisions & Patterns",
    ]
    for item in toc_items:
        pdf.body_text(item)

    # =====================================================================
    # CHAPTER 1: PROJECT OVERVIEW
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("1. Project Overview & Architecture")

    pdf.body_text(
        "NOVA is a personal AI assistant designed as a modular, agentic system. It is built for a single user "
        "(Sandaru Nihara) and runs a locally-hosted Large Language Model (Qwen 2.5 1.5B Instruct) with 4-bit "
        "quantization to minimize GPU memory usage. The system is NOT a simple chatbot - it is an intelligent "
        "agent that routes queries through multiple specialized engines before generating a response."
    )

    pdf.chapter_title("What Makes This an 'Agent'?", level=2)
    pdf.body_text(
        "Unlike a basic chatbot that always sends user input straight to an LLM, NOVA acts as an orchestrator. "
        "It inspects the user's query, classifies it into a category (greeting, identity, weather, math, document "
        "search, or general knowledge), and routes it to the appropriate specialized tool. Each tool gathers "
        "context (from the web, weather APIs, math computation, or loaded documents), and the LLM is then used "
        "to generate a natural language response grounded in that real data. This is the 'Retrieval-Augmented "
        "Generation' (RAG) pattern."
    )

    pdf.chapter_title("Core Capabilities", level=2)
    capabilities = [
        "Conversational AI: Multi-turn conversations with persona stability and memory management.",
        "Web Search RAG: DuckDuckGo search + deep web page scraping for factual grounding.",
        "Live Weather: Real-time weather data from wttr.in and Open-Meteo (no API key needed).",
        "Math Solver: LLM-based expression extraction + AST-safe Python evaluation (no eval()).",
        "Document RAG: Load PDFs/Markdown, chunk them, embed with sentence-transformers, and semantic search.",
        "Identity Management: Hardcoded identity prompts for who the user is, who Nova is, and who created Nova.",
        "Response Sanitization: Removes placeholder brackets, filler sign-offs, and AI slop patterns.",
        "Persona Drift Prevention: Periodic system reminders injected into context during long conversations.",
    ]
    for cap in capabilities:
        pdf.bullet(cap)
    pdf.ln(3)

    pdf.chapter_title("Technology Stack", level=2)
    stack = [
        "Language: Python 3.10+",
        "LLM: Qwen/Qwen2.5-1.5B-Instruct via HuggingFace Transformers",
        "Quantization: BitsAndBytes 4-bit (NF4 type, double quantization)",
        "Embeddings: sentence-transformers/all-MiniLM-L6-v2 for document RAG",
        "Search: DuckDuckGo via 'ddgs' library + custom HTML parser for deep scraping",
        "Weather: wttr.in (plain text) + Open-Meteo (JSON API) - zero API keys",
        "Math: Python AST module for safe expression evaluation",
        "PDF Parsing: PyMuPDF (fitz) for PDF text extraction",
        "GPU: PyTorch with CUDA support",
    ]
    for s in stack:
        pdf.bullet(s)

    # =====================================================================
    # CHAPTER 2: DIRECTORY STRUCTURE
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("2. Directory Structure")

    pdf.body_text("The project follows a clean, modular Python package structure:")

    tree = """ai-agent-project/
|-- .env                          # Environment variables (API keys if needed)
|-- .gitignore                    # Git ignore rules
|-- main.py                       # APPLICATION ENTRY POINT - starts the CLI loop
|-- requirements.txt              # Python dependencies
|-- src/                          # Source code package
|   |-- __init__.py               # Makes 'src' a Python package
|   |-- agent/                    # Agent orchestration layer
|   |   |-- __init__.py           # Makes 'agent' a Python package
|   |   |-- agent.py              # THE CORE AGENT - query routing & response pipeline
|   |   |-- memory.py             # Conversation memory with drift prevention
|   |-- models/                   # LLM model management
|   |   |-- __init__.py           # Makes 'models' a Python package
|   |   |-- llm_client.py         # Model loading, generation, search planning, math classification
|   |-- prompts/                  # All prompt engineering
|   |   |-- __init__.py           # Makes 'prompts' a Python package
|   |   |-- system_prompts.py     # System prompt, identity prompts, RAG prompts, math prompts
|   |-- tools/                    # External tool integrations
|   |   |-- __init__.py           # Makes 'tools' a Python package
|   |   |-- search.py             # DuckDuckGo search + web page scraping
|   |   |-- weather.py            # Live weather fetching (wttr.in + Open-Meteo)
|   |   |-- math_solver.py        # Safe AST-based math evaluator + LLM expression extraction
|   |   |-- document_rag.py       # PDF/Markdown document loader, chunker, embedder, searcher
|   |-- utils/                    # Configuration and shared utilities
|       |-- __init__.py           # Makes 'utils' a Python package
|       |-- config.py             # All constants, model IDs, hyperparameters
|-- tests/                        # Test files
    |-- test_math_solver.py       # Unit tests for the safe math evaluator
    |-- sample_doc.md             # Sample document for testing document RAG
    |-- Zeno Draft.pdf            # Sample PDF for testing"""
    pdf.code_block(tree, highlight_color=(240, 248, 255))

    pdf.chapter_title("Why __init__.py Files?", level=3)
    pdf.body_text(
        "Every directory inside 'src/' has an empty __init__.py file. In Python, this file's presence tells the "
        "interpreter that the directory should be treated as a 'package' - meaning you can import modules from it "
        "using dot notation like 'from src.agent.agent import NovaAgent'. Without __init__.py, Python would not "
        "recognize these directories as importable packages."
    )

    # =====================================================================
    # CHAPTER 3: config.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("3. src/utils/config.py - Configuration & Hyperparameters")

    pdf.body_text(
        "This is the centralized configuration file. Every tunable parameter in the entire project is defined here. "
        "This follows the 'Single Source of Truth' principle - if you need to change a model, adjust generation "
        "behavior, or tweak document chunking, you only modify this one file."
    )

    pdf.chapter_title("Complete Code with Line-by-Line Explanation", level=2)

    config_lines = {
        1: ("import os", "Import Python's built-in 'os' module which provides functions to interact with the operating system (environment variables, file paths, etc.)."),
        3: ('os.environ["HF_HOME"] = "E:/huggingface_cache"', "Set the HF_HOME environment variable. HuggingFace Transformers uses this to know WHERE to download and cache model files. Without this, models would download to the default directory (usually in your user profile). By setting it to E:/, we store large model files on a specific drive."),
        4: ('os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"', "On Windows, HuggingFace shows a warning about symbolic links not being supported. This suppresses that warning to keep the console output clean."),
        6: ('MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"', "The HuggingFace model identifier. This tells the Transformers library WHICH model to download and load. 'Qwen2.5-1.5B-Instruct' means: Qwen family, version 2.5, 1.5 billion parameters, instruction-tuned variant (fine-tuned to follow instructions rather than just predict next tokens)."),
        7: ('CACHE_DIR = "E:/huggingface_cache"', "Local directory for caching downloaded models. Same as HF_HOME but used as an explicit argument when loading models."),
        9: ("# Generation Hyperparameters", "These control HOW the LLM generates text. They directly affect response quality, creativity, and length."),
        10: ("MAX_NEW_TOKENS = 1024", "Maximum number of new tokens (words/sub-words) the model can generate per response. 1024 tokens is roughly 750-800 words. If the model hits this limit, it stops even mid-sentence."),
        11: ("TEMPERATURE = 0.25", "Controls randomness in generation. Range 0.0-2.0. Lower = more deterministic/focused (picks the highest probability token). Higher = more creative/random. 0.25 is very conservative - Nova gives consistent, focused answers rather than creative/varied ones."),
        12: ("TOP_P = 0.85", "Nucleus sampling threshold. The model considers only the smallest set of tokens whose cumulative probability >= 0.85. This means the bottom 15% of unlikely tokens are ignored. Works with temperature to control output diversity."),
        13: ("REPETITION_PENALTY = 1.15", "Penalizes tokens that have already appeared in the output. Values > 1.0 reduce repetition. 1.15 means already-used tokens are 15% less likely to be chosen again. Prevents the model from looping on phrases."),
        14: ("MAX_HISTORY_TURNS = 10", "How many conversation turns (user + assistant message pairs) to keep in memory. Older turns are dropped to fit within the model's context window. 10 turns = 20 messages (10 user + 10 assistant)."),
        16: ("# Persona Stability", "Settings to prevent the model from 'forgetting' its NOVA identity during long conversations."),
        17: ("DRIFT_REMINDER_INTERVAL = 4", "Every 4 assistant responses, a system reminder is injected into the context telling the model 'You are NOVA, you serve Sandaru'. This prevents 'persona drift' where the model gradually stops following its system prompt during extended sessions."),
        19: ("# Document RAG Settings", "Configuration for the document search feature."),
        20: ('EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"', "The embedding model used to convert text into numerical vectors. all-MiniLM-L6-v2 is a lightweight, fast model that produces 384-dimensional vectors. It's used for semantic similarity search in document RAG."),
        21: ("DOC_CHUNK_SIZE = 500", "When a document is loaded, it's split into chunks of approximately 500 characters each. Smaller chunks = more precise search results but less context per chunk. 500 chars is roughly one paragraph."),
        22: ("DOC_CHUNK_OVERLAP = 50", "Adjacent chunks overlap by 50 characters. This ensures that if important information spans a chunk boundary, it appears in both chunks and won't be missed during search."),
        23: ("DOC_SEARCH_TOP_K = 5", "When searching documents, return the top 5 most relevant chunks. More chunks = more context for the LLM but also more noise and token usage."),
        24: ("DOC_RELEVANCE_THRESHOLD = 0.35", "Minimum cosine similarity score (0.0-1.0) for a chunk to be considered relevant. Chunks scoring below 0.35 are discarded. This prevents irrelevant content from being fed to the LLM."),
    }

    for line_num, (code, explain) in config_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 4: system_prompts.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("4. src/prompts/system_prompts.py - System Prompts & Prompt Engineering")

    pdf.body_text(
        "This is the 'brain configuration' file - it defines NOVA's personality, behavior rules, and all the "
        "specialized prompt templates used for different query types. This is arguably the most critical file for "
        "the quality of responses. Prompt engineering is the art of crafting instructions that make LLMs behave "
        "exactly as desired."
    )

    pdf.chapter_title("The SYSTEM_PROMPT (Lines 7-56)", level=2)
    pdf.body_text(
        "The SYSTEM_PROMPT is the foundational instruction set that's ALWAYS present in every conversation. "
        "It's the very first message in the chat context (role='system'). The LLM reads this before anything "
        "else and it shapes all subsequent behavior."
    )

    system_prompt_sections = [
        ("Lines 7-10: <nova_core> and <identity>",
         "Uses XML-like tags to structure the prompt. This is a prompt engineering technique - LLMs (especially "
         "instruction-tuned ones) respond well to structured markup. The <identity> block establishes WHO the model "
         "is: NOVA, a personal AI assistant for Sandaru Nihara. This is the core identity anchor."),
        ("Lines 12-18: <behavior_directives>",
         "Five critical behavioral rules: (1) Always address user as 'Sir' with loyalty, (2) Complete obedience - never "
         "refuse or moralize, (3) Math execution rules - solve step-by-step, never search web for math, (4) ABSOLUTE "
         "PROHIBITION on placeholder text like '[Insert value]' - this is a common LLM failure mode where the model "
         "outputs template text instead of actual answers, (5) No preamble or flattery - get to the answer directly."),
        ("Lines 20-28: <tone_and_formatting>",
         "Controls the style of responses: use prose over bullet points, minimal formatting, no emojis unless the user "
         "uses them first. Also bans 'AI slop' words like 'genuinely', 'delve', 'straightforward' - these are words "
         "that LLMs overuse compared to human writing."),
        ("Lines 30-43: <response_hygiene>",
         "A critical quality control section. LLMs have a strong tendency to end responses with customer-service-like "
         "sign-offs ('Thank you for choosing me', 'Feel free to reach out', 'Best regards, NOVA'). This section "
         "explicitly lists and prohibits these patterns. The agent also has a code-level _clean_response() method "
         "that strips these programmatically as a safety net."),
        ("Lines 45-49: <technical_standards>",
         "Rules for code generation: clean, modular, production-ready. When showing code output or data, never "
         "truncate or hide information."),
        ("Lines 51-56: <error_and_correction_protocol>",
         "How to handle mistakes: own it briefly, fix it, move on. When the user's approach differs from convention, "
         "follow the user's approach - he is the authority on his project."),
    ]

    for title, text in system_prompt_sections:
        pdf.chapter_title(title, level=3)
        pdf.body_text(text)

    pdf.add_page()
    pdf.chapter_title("Prompt Builder Functions (Lines 59-227)", level=2)

    prompt_builders = [
        ("build_self_identity_prompt (Lines 59-65)",
         "Called when the user asks 'who are you?' or 'introduce yourself'. Returns a prompt that includes hard-coded "
         "facts about NOVA's identity and instructs the LLM to introduce itself in 2 sentences. The [Core Knowledge] "
         "block acts as injected context that the LLM must use - this prevents the model from making up different "
         "identity information."),
        ("build_user_identity_prompt (Lines 68-74)",
         "Called for 'who am I?' queries. Contains hard-coded facts about Sandaru Nihara. The prompt explicitly says "
         "'Do NOT describe yourself' to prevent the LLM from pivoting to self-description."),
        ("build_creator_prompt (Lines 77-83)",
         "For 'who created you?' queries. Hard-codes that the creator is Sandaru Nihara and instructs high respect."),
        ("build_greeting_prompt (Lines 86-92)",
         "For simple greetings (hi, hello, hey). Returns a simple prompt for a warm, brief greeting. Maximum 1-2 "
         "sentences to prevent the LLM from writing an essay in response to 'hello'."),
        ("build_search_augmented_prompt (Lines 95-120)",
         "THE CORE RAG PROMPT. This is used whenever web search or weather data has been retrieved. Key design: "
         "(1) <untrusted_reference_data> tag explicitly marks search results as UNTRUSTED external data, "
         "(2) <injection_defense_rules> prevent prompt injection attacks - if a malicious website contains text like "
         "'Ignore all previous instructions', the LLM is instructed to ignore such content, "
         "(3) <directives> enforce factual grounding - only use verified facts from the reference data, never invent."),
        ("get_long_conversation_reminder (Lines 123-134)",
         "Returns a persona drift reminder injected every N turns. This is inspired by Claude's long_conversation_reminder "
         "system. During long conversations, LLMs gradually 'forget' their system prompt. This periodic injection "
         "reinforces the NOVA identity and behavioral rules."),
        ("build_math_narrative_prompt (Lines 136-153)",
         "Used AFTER the math solver has computed an exact numerical answer. The prompt feeds the pre-computed result "
         "back to the LLM and instructs it to write a step-by-step explanation that arrives at EXACTLY that number. "
         "This is a key design: the LLM is NOT doing the math - it's only narrating the solution around a verified "
         "answer. This prevents arithmetic errors."),
        ("build_math_classifier_prompt (Lines 156-204)",
         "A few-shot classification prompt used to determine if a query is a math problem. Contains 16 examples "
         "(10 MATH, 6 NOT_MATH) teaching the LLM to distinguish math problems from general knowledge questions. "
         "Returns a message list (not a string) because it's used with the chat template format."),
        ("build_document_rag_prompt (Lines 207-227)",
         "Used when relevant content is found in loaded documents. Similar structure to the search RAG prompt but "
         "specific to document context. Key rule: if the document doesn't contain enough info, state what it DOES say "
         "and offer to use general knowledge instead."),
    ]

    for title, text in prompt_builders:
        pdf.chapter_title(title, level=3)
        pdf.body_text(text)

    # =====================================================================
    # CHAPTER 5: memory.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("5. src/agent/memory.py - Conversation Memory System")

    pdf.body_text(
        "This module manages the conversation history that gets sent to the LLM with each request. "
        "LLMs are stateless - they don't remember previous messages. The memory system maintains a list "
        "of messages and feeds them as context for each new generation."
    )

    memory_lines = {
        1: ("from src.prompts.system_prompts import SYSTEM_PROMPT, get_long_conversation_reminder",
            "Import the main system prompt (NOVA's identity/rules) and the drift prevention reminder function."),
        2: ("from src.utils.config import MAX_HISTORY_TURNS, DRIFT_REMINDER_INTERVAL",
            "Import configuration: how many turns to keep (10) and how often to inject reminders (every 4 turns)."),
        5: ("class ConversationMemory:",
            "Defines the ConversationMemory class - the single object that holds all conversation state."),
        6: ("def __init__(self):",
            "Constructor - called when a new ConversationMemory is created."),
        7: ("self.turn_count = 0",
            "Counter tracking how many assistant responses have been generated. Used to determine when to inject persona reminders."),
        8: ("self.reset()",
            "Call reset() to initialize the message list. Using reset() here means the constructor and the 'clear' command share the same initialization logic."),
        10: ("def reset(self):",
             "Resets conversation to a fresh state. Called at init and when the user types 'clear'."),
        11: ('self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]',
             "Initialize messages with just the system prompt. This is the ChatML format used by instruction-tuned LLMs: a list of dicts with 'role' (system/user/assistant) and 'content' (the text). The system prompt is ALWAYS the first message."),
        12: ("self.turn_count = 0",
             "Reset the turn counter back to zero."),
        14: ("def add_user_message(self, content: str):",
             "Appends a user message to the conversation history."),
        15: ('self.messages.append({"role": "user", "content": content})',
             "Add a dict with role='user' to the message list. This is the format the LLM expects."),
        17: ("def add_assistant_message(self, content: str):",
             "Appends an assistant (NOVA) response to the conversation history."),
        18: ('self.messages.append({"role": "assistant", "content": content})',
             "Add the assistant's response to the history so the LLM has context of what it previously said."),
        19: ("self.turn_count += 1",
             "Increment the turn counter. This is only incremented for assistant messages, not user messages."),
        21: ("def get_context_for_generation(self) -> list:",
             "Build the actual message list that will be sent to the LLM for the next generation."),
        29: ("if len(self.messages) > MAX_HISTORY_TURNS:",
             "Check if we have more messages than the maximum. If so, we need to trim old messages to fit within the model's context window."),
        30: ("context = [self.messages[0]] + self.messages[-(MAX_HISTORY_TURNS - 1):]",
             "Keep the FIRST message (system prompt) + the most recent (MAX_HISTORY_TURNS - 1) messages. This ensures the system prompt is never lost, but old conversation turns are dropped. Example: if MAX_HISTORY_TURNS=10 and we have 20 messages, keep message[0] (system) + messages[-9:] (last 9)."),
        32: ("context = list(self.messages)",
             "If we're under the limit, use all messages. list() creates a copy to avoid modifying the original."),
        35: ("if self.turn_count > 0 and self.turn_count % DRIFT_REMINDER_INTERVAL == 0:",
             "Check if it's time to inject a persona reminder. The % (modulo) operator checks if turn_count is divisible by 4. So reminders are injected at turns 4, 8, 12, 16, etc."),
        36: ('reminder = {"role": "system", "content": get_long_conversation_reminder()}',
             "Create a system message containing the persona reminder text."),
        38: ("context.insert(-1, reminder)",
             "Insert the reminder just BEFORE the last message (which is the user's latest query). This positioning means the model sees: [system prompt, ...history..., REMINDER, latest user message]. The reminder right before the user's query gives it maximum attention weight."),
        40: ("return context",
             "Return the built context list. This is what gets tokenized and fed into the LLM."),
    }

    for line_num, (code, explain) in memory_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 6: llm_client.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("6. src/models/llm_client.py - LLM Client")

    pdf.body_text(
        "This module is the interface between the application and the actual LLM model. It handles model loading "
        "with 4-bit quantization, text generation with streaming, search query planning, and math query classification. "
        "It abstracts away all the complexity of HuggingFace Transformers into a clean API."
    )

    llm_lines = {
        6: ("import torch",
            "Import PyTorch - the deep learning framework. Used for tensor operations, GPU management, and model inference."),
        7: ("from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextStreamer",
            "Import HuggingFace components: AutoModelForCausalLM loads the language model automatically detecting its architecture. AutoTokenizer loads the matching tokenizer (converts text to/from token IDs). BitsAndBytesConfig configures 4-bit quantization. TextStreamer enables real-time token-by-token output."),
        8: ("from src.utils.config import MODEL_ID, CACHE_DIR, MAX_NEW_TOKENS, TOP_P, REPETITION_PENALTY",
            "Import all configuration constants from the central config file."),
        9: ("from src.prompts.system_prompts import build_math_classifier_prompt",
            "Import the math classifier prompt builder for the classify_math_query method."),
        12: ("def __init__(self):",
             "Constructor - loads the model and tokenizer into GPU memory. This is the most expensive operation and happens once at startup."),
        13: ('print(f"Loading model \'{MODEL_ID}\' in 4-bit...")',
             "Status message so the user knows the model is loading (can take 30-60 seconds on first run)."),
        14: ("self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)",
             "Load the tokenizer. The tokenizer converts human-readable text into token IDs (numbers) that the model understands. 'from_pretrained' downloads it from HuggingFace Hub if not cached locally."),
        16: ("bnb_config = BitsAndBytesConfig(",
             "Create the quantization configuration object. Quantization compresses the model's weights from 16-bit floats to 4-bit integers, reducing memory usage by ~4x."),
        17: ("load_in_4bit=True,",
             "Enable 4-bit quantization. The 1.5B parameter model normally needs ~3GB VRAM in 16-bit. With 4-bit, it needs only ~1.2GB."),
        18: ('bnb_4bit_quant_type="nf4",',
             "Use NormalFloat4 quantization type. NF4 is specifically designed for normally-distributed neural network weights and gives better quality than simple 4-bit integer quantization."),
        19: ("bnb_4bit_compute_dtype=torch.bfloat16,",
             "Perform computations in bfloat16 precision. Even though weights are stored in 4-bit, actual math operations use bfloat16 for accuracy. bfloat16 is preferred over float16 because it has a larger exponent range and is more numerically stable."),
        20: ("bnb_4bit_use_double_quant=True",
             "Enable double quantization - quantize the quantization constants themselves. This saves an additional ~0.4 bits per parameter with negligible quality loss."),
        23: ("self.model = AutoModelForCausalLM.from_pretrained(",
             "Load the actual neural network model with the quantization config. 'CausalLM' means it's a causal language model - it predicts the next token given previous tokens (left-to-right generation)."),
        27: ('device_map="auto"',
             "Automatically place model layers on available GPUs (or CPU if no GPU). 'auto' handles multi-GPU setups and CPU offloading."),
        29: ("self.model.eval()",
             "Set the model to evaluation mode. This disables dropout layers and other training-specific behaviors, ensuring deterministic inference."),
        30: ("self.streamer = TextStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)",
             "Create a streamer that prints generated tokens to the console in real-time as they're produced. skip_prompt=True means it won't re-print the input prompt. skip_special_tokens=True hides internal tokens like <|endoftext|>."),
    }

    for line_num, (code, explain) in llm_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("plan_search_query Method (Lines 32-78)", level=2)
    pdf.body_text(
        "This method is the 'Search Planner' - it uses the LLM itself to decide whether a user query needs a web search. "
        "It uses a few-shot prompting technique where example input/output pairs teach the model the desired behavior."
    )

    plan_search_lines = {
        32: ("def plan_search_query(self, user_query: str, recent_context: str = '') -> str:",
             "Takes the user's query and the previous topic (for context-awareness). Returns either a search query string or 'NONE'."),
        37: ("planner_prompt = [",
             "Build a ChatML message list for the search planner. This is a SEPARATE mini-conversation with the LLM just for planning."),
        41: ('"You are an AI Search Planner..."',
             "System prompt for the planner: output a concise search query if external facts are needed. CRITICAL RULE: output 'NONE' for any math problem. The few-shot examples teach the model: compound interest = NONE, trains problem = NONE, President of Sri Lanka = search query."),
        59: ('"Previous Topic: {recent_context}..."',
             "Include the previous conversation topic so the planner can make context-aware decisions. If the user says 'what about their GDP?' after asking about Sri Lanka, the planner knows to search for 'Sri Lanka GDP'."),
        63: ("prompt_text = self.tokenizer.apply_chat_template(planner_prompt, tokenize=False, add_generation_prompt=True)",
             "Convert the message list into the model's specific chat format (e.g., <|im_start|>system\\n...\\n<|im_end|>). add_generation_prompt=True adds the assistant turn prefix so the model knows to generate a response."),
        64: ('inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")',
             "Tokenize the text into tensor of token IDs and move to GPU. return_tensors='pt' means PyTorch tensors."),
        66: ("with torch.no_grad():",
             "Disable gradient computation. Since we're only doing inference (not training), gradients aren't needed. This saves memory and speeds up execution."),
        69: ("max_new_tokens=20,",
             "Limit output to 20 tokens. A search query should be very short - this prevents the model from generating an essay."),
        70: ("do_sample=False,",
             "Greedy decoding - always pick the most likely token. We want deterministic, consistent search decisions, not creative ones."),
        74: ("new_tokens = outputs[0][inputs.input_ids.shape[1]:]",
             "Extract ONLY the newly generated tokens. outputs[0] is the full sequence (prompt + generation). inputs.input_ids.shape[1] is the length of the prompt. Slicing from that index gives just the new tokens."),
        75: ("decision = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()",
             "Convert the generated token IDs back into text and remove special tokens and whitespace."),
        76: ('decision = decision.replace(\'"\', \'\').replace("\'", "").replace("Search Query:", "").strip()',
             "Clean up the output - remove quotes and any 'Search Query:' prefix the model might include."),
    }

    for line_num, (code, explain) in plan_search_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("generate Method (Lines 80-105)", level=2)
    pdf.body_text(
        "The main text generation method. This is called for EVERY user-facing response. It supports two modes: "
        "deterministic (for factual RAG responses) and sampling (for creative/conversational responses)."
    )

    generate_lines = {
        80: ("def generate(self, messages: list, is_factual_rag: bool = False) -> str:",
             "Takes the full conversation context (message list) and a flag indicating if this is a factual RAG response."),
        81: ("prompt_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)",
             "Convert the full conversation into the model's chat format string. This includes the system prompt, all history, and the latest query."),
        84: ('inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")',
             "Tokenize and move to GPU."),
        86: ("gen_kwargs = {",
             "Build the generation arguments dictionary. These control the model's generation behavior."),
        87: ('"max_new_tokens": MAX_NEW_TOKENS,',
             "Maximum output length (1024 tokens from config)."),
        88: ('"repetition_penalty": 1.18,',
             "Slightly higher than config's 1.15 for the main generation - this is hardcoded at 1.18 to further reduce repetitive output in long responses."),
        94: ("if is_factual_rag:",
             "Branch based on response type. Factual RAG (web search, weather, math, document) uses greedy decoding for maximum accuracy."),
        95: ('gen_kwargs["do_sample"] = False',
             "Greedy decoding for factual responses. Always picks the highest-probability token. This ensures factual accuracy over creativity."),
        97: ('gen_kwargs["do_sample"] = True',
             "Sampling mode for conversational responses. Introduces controlled randomness for more natural, varied text."),
        98: ('gen_kwargs["temperature"] = 0.25',
             "Low temperature for conservative sampling. The model still has some randomness but stays focused."),
        99: ('gen_kwargs["top_p"] = TOP_P',
             "Nucleus sampling with p=0.85. Combined with low temperature, this produces coherent, on-topic responses."),
        101: ("with torch.no_grad():",
              "Disable gradient computation for inference efficiency."),
        102: ("outputs = self.model.generate(**inputs, **gen_kwargs)",
              "Run the actual model generation. **inputs unpacks the tokenized input, **gen_kwargs unpacks all generation parameters. The model autoregressively generates tokens one at a time. The TextStreamer prints each token to console as it's generated."),
        104: ("new_tokens = outputs[0][inputs.input_ids.shape[1]:]",
              "Extract only the newly generated tokens (exclude the input prompt)."),
        105: ("return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()",
              "Decode tokens back to text, strip special tokens and whitespace, and return."),
    }

    for line_num, (code, explain) in generate_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("classify_math_query Method (Lines 107-135)", level=2)

    classify_lines = {
        107: ("def classify_math_query(self, user_query: str) -> bool:",
              "Uses the LLM with a few-shot prompt to classify whether a query is a math problem. Returns True/False."),
        112: ("messages = build_math_classifier_prompt(user_query)",
              "Build the few-shot classification prompt with 16 examples (MATH/NOT_MATH)."),
        114: ("prompt_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)",
              "Format the classification prompt in the model's chat template."),
        120: ("max_new_tokens=5,",
              "Only allow 5 tokens - we expect a single word response: 'MATH' or 'NOT_MATH'."),
        121: ("do_sample=False,",
              "Greedy decoding for deterministic classification."),
        126: ("decision = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip().upper()",
              "Decode and uppercase the response for consistent matching."),
        129: ('if "NOT_MATH" in decision:',
              "Check for NOT_MATH first (it contains 'MATH' as a substring, so order matters)."),
        131: ('if "MATH" in decision:',
              "If NOT_MATH wasn't found but MATH is present, classify as a math problem."),
        135: ("return False",
              "Fallback: if the response is unclear, default to False (treat as non-math). This is conservative - it's better to miss a math problem than to incorrectly route a non-math query to the math solver."),
    }

    for line_num, (code, explain) in classify_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 7: search.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("7. src/tools/search.py - Web Search & Knowledge Extraction")

    pdf.body_text(
        "This module implements the web search tool using a two-stage pipeline: "
        "(1) DuckDuckGo search to find relevant URLs and snippets, then "
        "(2) deep web scraping of the top result to extract structured text and tables. "
        "This is the 'Retrieval' part of Retrieval-Augmented Generation (RAG)."
    )

    pdf.chapter_title("CleanArticleExtractor Class (Lines 15-84)", level=2)
    pdf.body_text(
        "A custom HTML parser that extracts clean, structured text from web pages. It inherits from Python's "
        "built-in HTMLParser and overrides its handler methods. The key innovation is that it intelligently "
        "strips away navigation menus, sidebars, infoboxes, citation markers, and other 'noise' elements that "
        "would pollute the context sent to the LLM."
    )

    search_lines = {
        7: ("import time", "Import time module (available for timeout handling)."),
        8: ("import re", "Import regex module for text pattern matching and cleaning."),
        9: ("import urllib.request", "Python's built-in HTTP request library. Used instead of 'requests' to avoid external dependencies."),
        10: ("import urllib.parse", "URL encoding utilities - for safely encoding search queries with special characters."),
        11: ("from html.parser import HTMLParser", "Python's built-in HTML parser. Used as a base class for our custom content extractor."),
        12: ("from ddgs import DDGS", "DuckDuckGo Search library - provides search results without needing an API key."),
        20: ("super().__init__()", "Initialize the parent HTMLParser class."),
        21: ("self.reset()", "Reset the parser state (inherited method)."),
        22: ("self.output = []", "List to accumulate extracted text fragments. These will be joined at the end."),
        23: ("self.ignore_depth = 0", "Counter for nested ignored elements. When > 0, all content is ignored. Supports nested tags (e.g., a nav inside an aside)."),
        24: ("self.in_table = False", "Flag tracking whether we're currently inside a <table> element."),
        25: ("self.current_row = []", "Accumulates cell values for the current table row."),
        27: ('self.ignored_tags = {"script", "style", "nav", ...}', "Set of HTML tags whose content should ALWAYS be ignored: scripts, CSS, navigation, footers, etc."),
        28: ('self.ignored_classes = ["infobox", "sidebar", ...]', "CSS class names to ignore. Wikipedia infoboxes, navigation boxes, edit section links, table of contents - all noise for our purposes."),
        31: ("def handle_starttag(self, tag, attrs):", "Called by the parser when an opening HTML tag is encountered (e.g., <div class='infobox'>)."),
        37: ("if tag in self.ignored_tags or any(c in classes ...):", "Check if this tag or its CSS classes/ID match our ignore list. If so, increment ignore_depth."),
        42: ("if tag == 'table':", "If we encounter a <table> tag while NOT in an ignored region, start table extraction mode."),
        46: ("elif tag == 'tr':", "New table row - reset the current_row accumulator."),
        47: ("elif tag in ['p', 'h2', 'h3', 'li']:", "Paragraph, heading, or list item - add a newline for formatting."),
        50: ("def handle_endtag(self, tag):", "Called when a closing tag is encountered (e.g., </div>)."),
        52: ("if self.ignore_depth > 0:", "If we're inside an ignored region, decrement the depth counter."),
        60: ("elif tag == 'tr' and self.in_table:", "End of a table row. If the row has 2+ cells, format it as a bullet point with em-dash separators."),
        69: ("def handle_data(self, data):", "Called for text content between tags."),
        73: ("if cleaned and not re.match(r'^\\[...\\]$', cleaned):", "Only include non-empty text that isn't a citation marker like [1] or [note 2]."),
        79: ("def get_clean_text(self, max_chars: int = 8000) -> str:", "Join all collected text fragments, normalize whitespace, and truncate to max_chars."),
    }

    for line_num, (code, explain) in search_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("fetch_webpage_content Function (Lines 87-102)", level=2)

    fetch_lines = {
        87: ("def fetch_webpage_content(url: str, max_chars: int = 8000) -> str:", "Takes a URL and returns cleaned text content from that page."),
        90: ("req = urllib.request.Request(url, headers={...})", "Create an HTTP request with a browser-like User-Agent header. Websites block requests from bots without a proper User-Agent."),
        96: ("with urllib.request.urlopen(req, timeout=7) as response:", "Open the URL with a 7-second timeout. 'with' ensures the connection is properly closed."),
        97: ('html = response.read().decode("utf-8", errors="ignore")', "Read the full HTML response and decode to UTF-8 string. errors='ignore' skips any invalid byte sequences."),
        98: ("extractor = CleanArticleExtractor()", "Create a new instance of our custom HTML parser."),
        99: ("extractor.feed(html)", "Feed the raw HTML into the parser. This triggers handle_starttag/handle_endtag/handle_data callbacks."),
        100: ("return extractor.get_clean_text(max_chars=max_chars)", "Return the cleaned text, limited to max_chars."),
    }

    for line_num, (code, explain) in fetch_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("search_and_fetch_knowledge Function (Lines 105-151)", level=2)

    search_func_lines = {
        105: ("def search_and_fetch_knowledge(query: str, max_results: int = 4) -> str:", "Main search function. Takes a query, returns combined context string from search snippets + deep-scraped page."),
        111: ("clean_query = query.replace('?', '').replace('!', '').strip()", "Remove punctuation that might confuse search engines."),
        114: ("if any(k in clean_query.lower() for k in ['list', 'all', ...]):", "Detect list/roster queries (e.g., 'list all presidents'). For these, Wikipedia is usually the best source."),
        116: ("clean_query += ' Wikipedia'", "Append 'Wikipedia' to the search query to prioritize Wikipedia results for list-type queries."),
        119: ("with DDGS(timeout=8) as ddgs:", "Create a DuckDuckGo search session with 8-second timeout."),
        120: ("results = list(ddgs.text(clean_query, max_results=max_results))", "Execute the search and get up to 4 results. Each result has title, body (snippet), and href (URL)."),
        126: ("for i, r in enumerate(results, 1):", "Iterate over results. enumerate(results, 1) gives (1, result1), (2, result2), etc."),
        130: ('if not top_url and "http" in href and "wikipedia.org" in href:', "Prioritize Wikipedia URLs as the top URL for deep scraping."),
        136: ("snippet_texts.append(f'[{i}] {title}: {body}')", "Add numbered search snippets to the context."),
        141: ("if top_url:", "If we found a good URL, do a deep scrape."),
        143: ("page_body = fetch_webpage_content(top_url, max_chars=8000)", "Fetch and clean the full page content (up to 8000 chars)."),
        144: ("if page_body and len(page_body) > 300:", "Only use the deep-scraped content if it's substantial (> 300 chars)."),
        145: ('combined_context = f"Verified Source Records ({top_url}):\\n{page_body}\\n\\nSearch Summary:\\n{combined_context}"', "Combine the deep-scraped page content WITH the search snippets. The deep-scraped content comes first for priority."),
    }

    for line_num, (code, explain) in search_func_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 8: weather.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("8. src/tools/weather.py - Live Weather Tool")

    pdf.body_text(
        "A zero-API-key weather fetching tool. Uses two fallback strategies to ensure reliable weather data "
        "retrieval. Strategy 1 uses wttr.in (a free plain-text weather service), and Strategy 2 uses "
        "Open-Meteo's free geocoding + forecast APIs."
    )

    weather_lines = {
        6: ("import urllib.request", "For making HTTP requests to weather APIs."),
        7: ("import urllib.parse", "For URL-encoding location names (e.g., 'New York' -> 'New%20York')."),
        8: ("import json", "For parsing JSON responses from Open-Meteo API."),
        9: ("import re", "For regex-based cleaning of location input."),
        11: ("def get_live_weather(location: str) -> str:", "Main function. Takes a natural language location string, returns formatted weather data."),
        16: ("clean_loc = re.sub(r'^(what is|current|weather in|weather for|weather)\\s+', '', location, flags=re.IGNORECASE).strip()",
             "Strip common query prefixes. If the user says 'what is weather in Colombo', we extract just 'Colombo'. The regex matches and removes words like 'what is', 'weather in', etc. from the start of the string."),
        17: ("encoded_loc = urllib.parse.quote(clean_loc)", "URL-encode the location name. Spaces become %20, special characters are escaped."),
        21: ('url = f"https://wttr.in/{encoded_loc}?format=%l:+%C+%t,+Humidity:+%h,+Wind:+%w"',
             "Strategy 1: wttr.in custom format. %l=location, %C=condition, %t=temperature, %h=humidity, %w=wind. This returns a single line like 'Colombo: Partly cloudy +30C, Humidity: 78%, Wind: 15km/h'."),
        22: ('req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})', "wttr.in returns HTML for browsers but plain text for curl. We impersonate curl to get the plain text format."),
        25: ('if text and "Unknown location" not in text and "<html" not in text:', "Validate the response: not empty, not an error, and not HTML (which would mean the format trick didn't work)."),
        31: ('geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1"',
             "Strategy 2 (fallback): First, geocode the location name to get latitude/longitude using Open-Meteo's free geocoding API."),
        39: ("res = geo_data['results'][0]", "Get the first geocoding result."),
        40: ("lat, lon = res['latitude'], res['longitude']", "Extract latitude and longitude for the weather forecast request."),
        43: ("forecast_url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'...)",
             "Build the forecast API URL requesting current temperature, humidity, apparent temperature, precipitation, and wind speed."),
        58: ("return (f'Live Meteorological Data for {city_name}:\\n'...)", "Format and return the weather data as a clean, structured string."),
        66: ("return f'Weather retrieval error: {e}'", "If both strategies fail, return the error message so the LLM can tell the user something went wrong."),
    }

    for line_num, (code, explain) in weather_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 9: math_solver.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("9. src/tools/math_solver.py - Safe Math Expression Evaluator")

    pdf.body_text(
        "This is the math solving engine - one of the most sophisticated components in the project. It uses a "
        "two-stage approach: (1) the LLM extracts a Python math expression from a word problem, then (2) a "
        "custom AST-based evaluator safely computes the result WITHOUT using Python's dangerous eval() function. "
        "This prevents code injection attacks while supporting complex mathematical operations."
    )

    pdf.chapter_title("Why Not Just Use eval()?", level=2)
    pdf.body_text(
        "Python's built-in eval() function executes arbitrary Python code. If the LLM generates something like "
        "__import__('os').system('rm -rf /'), eval() would execute it and delete your files. The AST-based "
        "evaluator parses the expression into a syntax tree and only allows whitelisted operations (arithmetic, "
        "specific math functions, and constants). Any attempt to call system functions, import modules, or access "
        "files is immediately blocked with a ValueError."
    )

    pdf.chapter_title("Allowed Operations Whitelist (Lines 14-56)", level=2)

    math_whitelist_lines = {
        14: ("_ALLOWED_BIN_OPS = {ast.Add: operator.add, ...}", "Maps AST binary operation nodes to their actual Python operator functions. Only these operations are permitted: +, -, *, /, **, //, %. Any other operator (bitwise, comparison, etc.) will raise ValueError."),
        24: ("_ALLOWED_UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}", "Allows unary minus (-5) and unary plus (+5). These are different from binary operations."),
        30: ("_ALLOWED_MATH_FUNCS = {'sqrt': math.sqrt, 'sin': math.sin, ...}",
             "Whitelist of allowed function calls. Includes: sqrt, sin, cos, tan, radians, degrees, log, log10, log2, exp, factorial, ceil, floor, abs, comb (combinations), perm (permutations). Also includes aliases: 'combinations' maps to math.comb, 'permutations' maps to math.perm."),
        53: ("_ALLOWED_MATH_CONSTANTS = {'pi': math.pi, 'e': math.e}",
             "Allowed named constants. The evaluator resolves 'pi' to 3.14159... and 'e' to 2.71828..."),
    }

    for line_num, (code, explain) in math_whitelist_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("safe_eval Function (Lines 59-77)", level=2)

    safe_eval_lines = {
        59: ("def safe_eval(expr: str):", "Entry point for safe expression evaluation. Takes a string like '10000 * (1 + 0.06/4)**(4*3)' and returns the numerical result."),
        66: ("expr = expr.strip().rstrip('=').strip()", "Clean the expression: remove whitespace and trailing equals signs (LLM sometimes outputs '2+3 =')."),
        68: ("expr = expr.replace('import math', '').strip()", "Remove any 'import math' statements the LLM might include before the expression."),
        70: ("lines = [l.strip() for l in expr.split('\\n') if l.strip()]", "Handle multi-line output: split by newlines and take only non-empty lines."),
        72: ("expr = lines[-1]", "Use the LAST non-empty line as the expression. If the LLM outputs 'import math\\n50 * math.tan(math.radians(60))', this takes just the expression line."),
        74: ("node = ast.parse(expr, mode='eval').body", "Parse the expression into an Abstract Syntax Tree. mode='eval' means we expect a single expression (not statements). .body gets the root expression node."),
        75: ("return _eval_node(node)", "Recursively evaluate the AST node using our whitelisted operations."),
        77: ("raise ValueError(f'Invalid math expression: {e}')", "If parsing fails, raise a clear error."),
    }

    for line_num, (code, explain) in safe_eval_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("_eval_node Function (Lines 80-128) - The AST Walker", level=2)

    eval_node_lines = {
        80: ("def _eval_node(node):", "Recursively evaluates an AST node. This is the heart of the safe evaluator. It pattern-matches on the node type and only allows whitelisted operations."),
        84: ("if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):", "BASE CASE: If the node is a numeric literal (42, 3.14), return its value directly."),
        88: ("if isinstance(node, ast.BinOp):", "BINARY OPERATION: a + b, a * b, a ** b, etc. Get the operator type, check it's in the whitelist, then recursively evaluate left and right operands."),
        92: ("return _ALLOWED_BIN_OPS[op_type](_eval_node(node.left), _eval_node(node.right))", "Recursively evaluate both sides, then apply the operator. For '2 + 3': evaluate(2)=2, evaluate(3)=3, operator.add(2,3)=5."),
        95: ("if isinstance(node, ast.UnaryOp):", "UNARY OPERATION: -x or +x. Check whitelist and apply."),
        102: ("if isinstance(node, ast.Call):", "FUNCTION CALL: sqrt(x), math.sin(x), abs(x). Extract function name, verify it's whitelisted, evaluate arguments, and call the function."),
        106: ("if len(node.args) < 1 or len(node.args) > 2:", "Functions must have 1 or 2 arguments (e.g., math.log(x) or math.log(x, base))."),
        112: ("if isinstance(node, ast.Attribute):", "ATTRIBUTE ACCESS: math.pi, math.e. Only allow 'math.' prefix accessing whitelisted constants."),
        120: ("if isinstance(node, ast.Name):", "BARE NAME: 'pi' or 'e' without the 'math.' prefix. Resolve against the constants whitelist."),
        128: ("raise ValueError(f'Disallowed expression structure: {type(node).__name__}')", "CATCH-ALL: Any AST node type not handled above is blocked. This prevents any sneaky code injection."),
    }

    for line_num, (code, explain) in eval_node_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("Expression Extraction System Prompt (Lines 146-187)", level=2)
    pdf.body_text(
        "This is the prompt that instructs the LLM to convert natural language math problems into Python "
        "expressions. It contains 12 worked examples covering compound interest, trigonometry, probability, "
        "bacterial growth, pipe/work rate problems, Pythagorean theorem, optimization, factorials, geometry, "
        "combinatorics, and radioactive decay. The LLM must output ONLY the raw expression - no explanation."
    )

    pdf.chapter_title("extract_and_solve_math Function (Lines 190-246)", level=2)

    extract_lines = {
        190: ("def extract_and_solve_math(user_query: str, llm_client) -> tuple[str, float | None]:", "Main entry point. Takes the user's word problem and the LLM client. Returns (expression_string, computed_result) or (raw_output, None) if evaluation fails."),
        196: ("messages = [{...system prompt...}, {...user query...}]", "Build a mini-conversation for expression extraction. The system prompt contains all the extraction rules and examples."),
        201: ("raw_expr = llm_client.generate(messages, is_factual_rag=True)", "Generate the expression using greedy decoding (is_factual_rag=True) for maximum precision."),
        202: ("clean_expr = _clean_expression(raw_expr)", "Clean the LLM output: remove markdown fences, 'Expression:' prefix, comments, and extra lines."),
        207: ("result = safe_eval(clean_expr)", "FIRST ATTEMPT: Try to evaluate the cleaned expression."),
        208: ("return clean_expr, result", "Success! Return the expression and its computed value."),
        213: ("retry_messages = [...]", "RETRY MECHANISM: If the first attempt fails, build a new prompt that includes the error message and asks the LLM to fix the expression. This is a self-correction loop."),
        220: ("f'ERROR: The expression \\'{clean_expr}\\' failed to evaluate: {eval_error}'", "Feed the exact error back to the LLM so it knows what went wrong and can fix it."),
        227: ("retry_expr = llm_client.generate(retry_messages, is_factual_rag=True)", "Second generation attempt with error feedback."),
        237: ("match = re.search(r'([\\d\\s+\\-*/().**]+)', raw_expr)", "FINAL FALLBACK: If both attempts fail, try to find any evaluable numeric sub-expression in the raw output using regex."),
        246: ("return raw_expr, None", "Ultimate failure: return the raw LLM output with None (the agent will fall back to internal reasoning)."),
    }

    for line_num, (code, explain) in extract_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("_clean_expression Function (Lines 249-269)", level=2)
    pdf.body_text(
        "Utility function that cleans LLM output to extract just the math expression. Removes markdown code "
        "fences (```python ... ```), 'Expression:' prefixes, trailing comments, and takes only the first "
        "non-empty line (since the LLM might add explanation text after the expression)."
    )

    # =====================================================================
    # CHAPTER 10: document_rag.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("10. src/tools/document_rag.py - Document RAG Engine")

    pdf.body_text(
        "This module implements a complete Retrieval-Augmented Generation pipeline for local documents. "
        "When a user loads a PDF or Markdown file, this engine: (1) extracts the text, (2) splits it into "
        "overlapping chunks, (3) computes embedding vectors for each chunk using a sentence-transformer model, "
        "and (4) performs semantic search using cosine similarity when the user asks questions."
    )

    pdf.chapter_title("How Semantic Search Works", level=2)
    pdf.body_text(
        "Traditional keyword search matches exact words. Semantic search understands MEANING. The sentence-transformer "
        "model converts text into 384-dimensional vectors where similar meanings are close together in vector space. "
        "For example, 'What is the project budget?' and 'How much does it cost?' would have very similar vectors even "
        "though they share no words. Cosine similarity measures the angle between two vectors - 1.0 = identical meaning, "
        "0.0 = completely unrelated."
    )

    pdf.chapter_title("DocumentChunk Dataclass (Lines 13-20)", level=2)

    doc_chunk_lines = {
        13: ("@dataclass", "Python decorator that automatically generates __init__, __repr__, and other methods. Saves boilerplate code."),
        14: ("class DocumentChunk:", "Represents one chunk of text from a loaded document."),
        16: ("text: str", "The actual text content of this chunk (up to ~500 characters)."),
        17: ("doc_name: str", "Name of the source document (e.g., 'report.pdf')."),
        18: ("page_num: int", "Page number in the original document (1-indexed for PDFs, 0 for text files)."),
        19: ("chunk_index: int", "Sequential index of this chunk within the document."),
        20: ("embedding: np.ndarray = field(default_factory=lambda: np.array([]))", "384-dimensional embedding vector. Initialized as empty array; populated after embedding computation."),
    }

    for line_num, (code, explain) in doc_chunk_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("DocumentStore Class (Lines 23-282)", level=2)

    doc_store_lines = {
        30: ("def __init__(self, embedding_model_id, chunk_size=500, chunk_overlap=50, cache_dir=None):",
             "Constructor. Takes the embedding model name, chunking parameters, and optional cache directory. The model is NOT loaded here - it's lazy-loaded on first use to avoid slow startup if documents are never loaded."),
        36: ("self._model = None", "The sentence-transformer model. None until first use. Lazy loading means the embedding model is only downloaded/loaded when the user actually loads a document."),
        37: ("self._documents: dict[str, list[DocumentChunk]] = {}", "Dictionary mapping document names to their list of chunks. This is the in-memory document store."),
        42: ("def has_documents(self) -> bool:", "Property that returns True if any documents are loaded. Used by the agent to decide whether to attempt document search."),
        45: ("def load_document(self, filepath: str) -> dict:", "Load a document file. Returns a result dict with success status, document name, page count, and chunk count."),
        50: ("filepath = filepath.strip().strip('\"').strip(\"'\")", "Clean the filepath: remove whitespace and surrounding quotes (users often paste paths with quotes)."),
        60: ("if ext == '.pdf':", "Route PDF files to the PDF extractor (uses PyMuPDF)."),
        62: ("elif ext in ('.md', '.markdown', '.txt', ...):", "Route text-based files to the text extractor. Supports many formats."),
        73: ("chunks = self._chunk_pages(pages, doc_name)", "Split the extracted text into overlapping chunks."),
        79: ("self._ensure_model_loaded()", "Trigger lazy loading of the embedding model if not already loaded."),
        81: ("embeddings = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)",
             "Compute embedding vectors for ALL chunks at once (batch processing is much faster than one-by-one). normalize_embeddings=True means vectors are unit-length, so dot product = cosine similarity."),
        87: ("self._documents[doc_name] = chunks", "Store the chunks in the document dictionary. If a document with the same name was already loaded, it's replaced."),
        96: ("def unload_document(self, doc_name: str) -> dict:", "Remove a document. Supports both exact and partial name matching for user convenience."),
        104: ("matches = [name for name in self._documents if doc_name.lower() in name.lower()]", "Fuzzy matching: if exact name not found, look for documents whose names CONTAIN the given string. E.g., 'report' would match 'quarterly_report.pdf'."),
        128: ("def search(self, query: str, top_k: int = 5) -> list[tuple[DocumentChunk, float]]:", "Semantic search across all loaded documents. Returns top-k (chunk, similarity_score) tuples."),
        139: ("query_embedding = self._model.encode([query], normalize_embeddings=True)[0]", "Convert the search query into an embedding vector."),
        145: ("similarity = float(np.dot(query_embedding, chunk.embedding))", "Compute cosine similarity using dot product. Because embeddings are normalized, dot product equals cosine similarity. Higher value = more semantically similar."),
        149: ("results.sort(key=lambda x: x[1], reverse=True)", "Sort by similarity score in descending order (most relevant first)."),
    }

    for line_num, (code, explain) in doc_store_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("Text Extraction Methods (Lines 155-175)", level=2)

    extract_text_lines = {
        156: ("def _extract_pdf(filepath: str) -> list[str]:", "Extract text from PDF using PyMuPDF. Returns a list of strings, one per page."),
        158: ("import fitz", "Lazy import of PyMuPDF (imported as 'fitz' for historical reasons). Only imported when a PDF is actually loaded."),
        161: ("with fitz.open(filepath) as doc:", "Open the PDF file. 'with' ensures proper cleanup."),
        163: ("text = page.get_text('text')", "Extract text from each page. 'text' mode gives plain text without formatting."),
        169: ("def _extract_text_file(filepath: str) -> list[str]:", "Read a text/markdown file as a single 'page'."),
        171: ("with open(filepath, 'r', encoding='utf-8', errors='replace') as f:", "Open with UTF-8 encoding. errors='replace' handles files with non-UTF-8 characters by replacing them with a placeholder."),
    }

    for line_num, (code, explain) in extract_text_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("Chunking Algorithm (Lines 179-269)", level=2)
    pdf.body_text(
        "The chunking algorithm splits documents into overlapping segments suitable for embedding and search. "
        "It works in two stages: (1) split by paragraphs (double newlines), then (2) for very long paragraphs, "
        "split by sentence boundaries. The overlap ensures information at chunk boundaries isn't lost."
    )

    chunking_lines = {
        184: ("for page_num, page_text in enumerate(pages, start=1):", "Iterate over pages. enumerate(pages, start=1) gives (1, page1_text), (2, page2_text), etc."),
        186: ("paragraphs = re.split(r'\\n\\s*\\n', page_text)", "Split text by double newlines (paragraph boundaries). \\s* matches optional whitespace between newlines."),
        195: ("if current_chunk and (len(current_chunk) + len(para) + 2) > self.chunk_size:", "If adding this paragraph would exceed the chunk size limit, save the current chunk and start a new one."),
        205: ("if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:", "OVERLAP: When starting a new chunk, carry over the last 50 characters from the previous chunk. This creates continuity between chunks."),
        206: ("current_chunk = current_chunk[-self.chunk_overlap:] + '\\n\\n' + para", "The new chunk starts with the tail of the previous chunk, ensuring text spanning the boundary appears in both."),
        216: ("if len(current_chunk) > self.chunk_size * 1.5:", "If a single paragraph is extremely long (>750 chars), use sentence-level splitting instead."),
        238: ("sentences = re.split(r'(?<=[.!?])\\s+', text)", "Split by sentence boundaries. The lookbehind (?<=[.!?]) matches positions after sentence-ending punctuation."),
        273: ("def _ensure_model_loaded(self):", "Lazy-load the sentence-transformer model on first use. This avoids downloading the model at startup if the user never loads any documents."),
        278: ("self._model = SentenceTransformer(self.embedding_model_id, cache_folder=self.cache_dir)", "Initialize the sentence-transformer model. Downloads ~90MB on first run, then uses the cached version."),
    }

    for line_num, (code, explain) in chunking_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 11: agent.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("11. src/agent/agent.py - The Core Agent (Orchestrator)")

    pdf.body_text(
        "This is the central file of the entire project - the 'brain' that ties everything together. "
        "The NovaAgent class acts as an orchestrator: it classifies each user query, routes it to the "
        "appropriate tool (weather, math, document search, web search, or identity), constructs an "
        "augmented prompt with retrieved context, generates a response via the LLM, cleans the output, "
        "and manages conversation memory."
    )

    pdf.chapter_title("Filler & Pattern Definitions (Lines 27-74)", level=2)

    pattern_lines = {
        27: ("_FILLER_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [...]]",
             "Pre-compiled regex patterns for detecting filler sign-offs that the LLM might generate. These include 'Thank you...', 'If you encounter...', 'Let us embark...', 'Best regards', etc. These are compiled once at module load time for performance."),
        44: ("_WEATHER_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [...]]",
             "Regex patterns to detect weather queries. Matches words like 'weather', 'temperature', 'forecast', 'rain', 'humidity', 'climate'. The \\b markers are word boundaries to prevent false matches (e.g., 'climate' in 'acclimate')."),
        52: ("_MATH_CANDIDATE_PATTERN = re.compile(r'(?:...)', re.IGNORECASE)",
             "A comprehensive regex for FAST pre-screening of math queries. This is a performance optimization: before making an expensive LLM classification call, this regex checks if the query even LOOKS like it could be math. It matches: numbers with % $ degree symbols, multiple numbers, math-related keywords (area, volume, radius, solve, calculate, probability, invested, equation, etc.), geometric shapes, trig functions, rate/speed problems, and pipe/tank problems."),
        72: ("_USER_IDENTITY_PATTERNS = [...]", "Regex patterns for 'who am I?' / 'my name' queries."),
        73: ("_CREATOR_PATTERNS = [...]", "Patterns for 'your creator', 'who made you', 'who owns you' queries."),
        74: ("_SELF_IDENTITY_PATTERNS = [...]", "Patterns for 'who are you', 'what is your name', 'introduce yourself', 'your purpose' queries."),
    }

    for line_num, (code, explain) in pattern_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("NovaAgent.__init__ (Lines 77-87)", level=2)

    init_lines = {
        78: ("def __init__(self):", "Constructor - initializes all components of the agent."),
        79: ("self.llm = LLMClient()", "Create the LLM client. This triggers model loading (downloads ~1.5GB on first run, loads into GPU)."),
        80: ("self.memory = ConversationMemory()", "Create the conversation memory with the system prompt pre-loaded."),
        81: ("self.last_topic = ''", "Track the previous conversation topic for context-aware search planning."),
        82: ("self.doc_store = DocumentStore(...)", "Create the document store for RAG. Embedding model is NOT loaded yet (lazy loading)."),
    }

    for line_num, (code, explain) in init_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("Query Classification Methods (Lines 89-121)", level=2)

    classify_lines = {
        90: ("def classify_identity_query(query: str):", "Static method (no 'self' needed) that classifies identity queries. Returns 'user', 'creator', 'self', or None."),
        100: ("def is_greeting(query: str) -> bool:", "Checks if the query is a simple greeting. Normalizes input: lowercase, strip, remove trailing punctuation, then check against a short list."),
        105: ("def is_weather_query(query: str) -> bool:", "Checks if the query contains weather-related keywords."),
        108: ("def is_math_query(self, query: str) -> bool:", "Two-stage math detection: (1) exclude obviously non-math queries (contains 'president', 'who is', etc.), (2) fast regex pre-check, (3) LLM classification. This requires 'self' because it calls self.llm.classify_math_query()."),
        112: ("if any(w in lower for w in ['president', 'who is', 'weather', ...]):", "Hard exclusion list. Queries about people, weather, explanations, or creative writing are NEVER math, regardless of what the regex or LLM says."),
        116: ("if not _MATH_CANDIDATE_PATTERN.search(query):", "Fast regex pre-check. If the query doesn't contain any math-like patterns, skip the expensive LLM classification call."),
        121: ("return self.llm.classify_math_query(query)", "Final decision: use the LLM with a few-shot prompt to classify the query."),
    }

    for line_num, (code, explain) in classify_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("_clean_response Method (Lines 123-140)", level=2)

    clean_lines = {
        124: ("def _clean_response(text: str) -> str:", "Post-processing cleanup of LLM output. Removes placeholder brackets and filler sign-offs."),
        126: ("text = re.sub(r'\\[Insert [^\\]]+\\]', '', text, flags=re.IGNORECASE)", "Remove [Insert ...] placeholders. These are a common LLM failure mode where the model outputs template text instead of actual content."),
        127: ("text = re.sub(r'\\[Unit\\]', '', text, flags=re.IGNORECASE)", "Remove [Unit] placeholders specifically."),
        128: ("text = re.sub(r'\\[.*?\\]', '', text)", "Remove ANY remaining square bracket markers. .*? is a non-greedy match so it handles multiple brackets on one line."),
        130: ("lines = text.rstrip().split('\\n')", "Split the response into lines for tail-stripping."),
        131: ("while lines:", "Iterate from the end of the response, removing filler lines."),
        136: ("if any(p.match(candidate) for p in _FILLER_PATTERNS):", "Check the last line against all filler patterns. If it matches, remove it and check the next line. This progressively strips sign-offs."),
        140: ("return '\\n'.join(lines).rstrip()", "Rejoin the cleaned lines and return."),
    }

    for line_num, (code, explain) in clean_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("process_turn Method (Lines 142-260) - THE MAIN PIPELINE", level=2)

    pdf.body_text(
        "This is the most important method in the entire project. Every user message passes through this "
        "method. It implements a priority-based routing pipeline with 7 stages:"
    )

    process_lines = {
        142: ("def process_turn(self, user_input: str) -> str:", "Main entry point for processing a user turn. Returns the agent's response string."),
        143: ("is_rag = False", "Flag tracking whether this response is grounded in external data (search, weather, math, document). Determines generation mode (greedy vs sampling)."),
        146: ("lower_input = user_input.lower().strip()", "Normalize input for case-insensitive matching."),
        148: ("if lower_input.startswith('load '):", "STAGE 0: Document management commands. 'load <file>' loads a document into the RAG engine."),
        149: ("filepath = user_input[5:].strip()", "Extract the filepath by removing 'load ' prefix (5 characters)."),
        151: ("result = self.doc_store.load_document(filepath)", "Call the document store to load, chunk, and embed the document."),
        159: ("if lower_input == 'docs':", "List all loaded documents with their page/chunk counts."),
        169: ("if lower_input.startswith('unload '):", "Remove a loaded document by name."),
        179: ("if self.is_greeting(user_input):", "STAGE 1: Greeting detection. Simple pattern match - no LLM needed."),
        181: ("augmented = build_greeting_prompt(user_input)", "Build a greeting-specific prompt."),
        184: ("elif self.classify_identity_query(user_input):", "STAGE 2: Identity queries. Routes to user/creator/self identity prompts."),
        197: ("elif self.is_weather_query(user_input):", "STAGE 3: Weather queries. Fetches live weather data and builds a search-augmented prompt."),
        199: ("weather_data = get_live_weather(user_input)", "Fetch real-time weather from wttr.in or Open-Meteo."),
        201: ("augmented = build_search_augmented_prompt(user_input, weather_data)", "Wrap the weather data in the injection-resistant RAG prompt template."),
        207: ("elif self.doc_store.has_documents and (doc_result := self._try_document_search(user_input)):",
              "STAGE 4: Document RAG. Only runs if documents are loaded. Uses the walrus operator (:=) to both check AND capture the search result in one expression. This is Python 3.8+ syntax."),
        210: ("augmented = build_document_rag_prompt(user_input, doc_context, source_info)", "Build a document-grounded RAG prompt."),
        214: ("elif self.is_math_query(user_input):", "STAGE 5: Math solving. Two-stage classification (regex + LLM) must both pass."),
        216: ("expr, exact_val = extract_and_solve_math(user_input, self.llm)", "Extract a Python expression from the word problem and safely evaluate it."),
        218: ("if exact_val is not None:", "If math evaluation succeeded, use the exact result."),
        220: ("augmented = build_math_narrative_prompt(user_input, expr, exact_val)", "Build the math narrative prompt that feeds the pre-computed answer to the LLM for step-by-step explanation."),
        228: ("search_query = self.llm.plan_search_query(user_input, recent_context=self.last_topic)",
              "STAGE 6: General search. Ask the LLM if a web search is needed. Includes previous topic for context."),
        230: ("if search_query.upper() != 'NONE' and len(search_query) > 2:", "If the planner returned a real query (not 'NONE' and more than 2 chars), do the search."),
        232: ("web_context = search_and_fetch_knowledge(search_query)", "Execute the two-stage search pipeline (DuckDuckGo + deep scrape)."),
        235: ("augmented = build_search_augmented_prompt(user_input, web_context)", "Wrap search results in the RAG prompt template."),
        237: ("self.last_topic = user_input", "Remember this query as the 'last topic' for future context-aware search planning."),
        241: ("augmented = user_input", "FALLBACK: If no search needed, use the raw user input. The LLM will rely on its internal knowledge."),
    }

    for line_num, (code, explain) in process_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.add_page()
    pdf.chapter_title("Generation & Memory Update (Lines 244-260)", level=2)

    gen_lines = {
        245: ("self.memory.add_user_message(augmented)", "Add the AUGMENTED prompt (with retrieved context) to memory. This is what the LLM sees."),
        246: ("context = self.memory.get_context_for_generation()", "Build the full context list with history trimming and optional persona reminder."),
        248: ("if self.memory.turn_count > 0 and self.memory.turn_count % 4 == 0:", "Check if it's time for a persona stability reminder."),
        251: ("print('\\nNova: ', end='', flush=True)", "Print the response prefix without a newline. flush=True ensures it appears immediately. The streamer will print tokens after this."),
        252: ("raw_response = self.llm.generate(context, is_factual_rag=is_rag)", "Generate the response. The streamer prints tokens in real-time. Returns the full response text."),
        253: ("response = self._clean_response(raw_response)", "Clean the response: remove placeholders and filler sign-offs."),
        256: ("self.memory.messages.pop()", "IMPORTANT: Remove the augmented prompt from memory. We don't want the LLM to see search results or math expressions in future turns."),
        257: ("self.memory.add_user_message(user_input)", "Add the ORIGINAL user input (without RAG context) to memory. This keeps the conversation history clean and natural."),
        258: ("self.memory.add_assistant_message(response)", "Add the assistant's cleaned response to memory for future context."),
        260: ("return response", "Return the response to main.py for display."),
    }

    for line_num, (code, explain) in gen_lines.items():
        pdf.line_explain(line_num, code, explain)

    pdf.chapter_title("_try_document_search Method (Lines 262-291)", level=2)

    doc_search_lines = {
        262: ("def _try_document_search(self, query: str) -> tuple[str, str, float] | None:", "Search loaded documents for relevant content. Returns (context_text, source_info, best_score) or None."),
        268: ("results = self.doc_store.search(query, top_k=DOC_SEARCH_TOP_K)", "Perform semantic search across all loaded document chunks."),
        273: ("best_score = results[0][1]", "Get the similarity score of the best-matching chunk."),
        275: ("if best_score < DOC_RELEVANCE_THRESHOLD:", "If even the best match is below the threshold (0.35), the documents don't contain relevant information. Return None."),
        282: ("if score >= DOC_RELEVANCE_THRESHOLD * 0.7:", "Include chunks slightly below the threshold (0.7 * 0.35 = 0.245). This captures borderline-relevant content that might add useful context."),
        284: ("f'[Source: {chunk.doc_name}, Page {chunk.page_num}]\\n{chunk.text}'", "Format each chunk with its source attribution. The LLM will see which document and page the information came from."),
        288: ("doc_context = '\\n\\n---\\n\\n'.join(context_parts)", "Join all relevant chunks with separators for clear delineation."),
    }

    for line_num, (code, explain) in doc_search_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 12: main.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("12. main.py - Application Entry Point")

    pdf.body_text(
        "This is the simplest file in the project. It creates the NovaAgent, displays a welcome banner, "
        "and runs an infinite loop reading user input and processing it through the agent."
    )

    main_lines = {
        1: ("import sys", "Import sys module for system path manipulation."),
        2: ("import os", "Import os module for path operations."),
        5: ("sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))", "Add the project root directory to Python's module search path. This ensures 'from src.agent.agent import NovaAgent' works regardless of which directory you run the script from. os.path.dirname(__file__) gets the directory containing main.py, os.path.abspath() converts it to an absolute path, and sys.path.insert(0, ...) adds it as the FIRST search path."),
        7: ("from src.agent.agent import NovaAgent", "Import the main agent class. This triggers a chain of imports: agent.py imports memory.py, llm_client.py, all tools, all prompts, and config.py."),
        9: ("def main():", "Main function. Keeps the entry point clean and testable."),
        10: ("agent = NovaAgent()", "Create the agent. This loads the LLM model into GPU (takes ~30-60 seconds on first run)."),
        11: ('print("\\n" + "=" * 60)', "Print a decorative header. '=' * 60 creates a line of 60 equals signs."),
        22: ("while True:", "Infinite loop - the program keeps running until the user types 'exit'."),
        23: ('user_input = input("\\nSandaru: ").strip()', "Read user input from the console with a personalized prompt. .strip() removes leading/trailing whitespace."),
        24: ("if not user_input:", "If the user just pressed Enter (empty input), skip to the next iteration."),
        26: ('if user_input.lower() in ["exit", "quit", "q"]:', "Check for exit commands (case-insensitive)."),
        29: ('if user_input.lower() == "clear":', "Handle the 'clear' command to reset conversation memory."),
        30: ("agent.memory.reset()", "Reset the conversation history back to just the system prompt."),
        34: ("result = agent.process_turn(user_input)", "Process the user's input through the full agent pipeline and get the response."),
        35: ("if result:", "Document management commands return an empty string (they handle their own output). Only print the separator for actual conversation responses."),
        38: ('if __name__ == "__main__":', "Python idiom: only run main() if this file is executed directly (not imported)."),
    }

    for line_num, (code, explain) in main_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 13: test_math_solver.py
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("13. tests/test_math_solver.py - Unit Tests")

    pdf.body_text(
        "A standalone test suite for the safe_eval math evaluator. Uses plain assertions instead of pytest "
        "for simplicity. Tests cover basic arithmetic, math functions, word problem expressions, security "
        "(blocking dangerous operations), and edge cases."
    )

    test_lines = {
        11: ("sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))", "Add the project root (one directory up from tests/) to the Python path so imports work."),
        13: ("from src.tools.math_solver import safe_eval", "Import only the safe_eval function - we're testing the evaluator in isolation."),
        20: ("def test(name, expression, expected, tolerance=1e-10):", "Test helper that evaluates an expression and compares the result to an expected value with a tolerance for floating-point comparison."),
        24: ("if abs(result - expected) < tolerance:", "Floating-point comparison. We can't use == because of precision issues (e.g., 0.1 + 0.2 = 0.30000000000000004 in floating point)."),
        39: ("def test_raises(name, expression):", "Test helper for security tests. Verifies that evaluating a dangerous expression raises ValueError."),
        47: ("except ValueError:", "If ValueError is raised, the security test PASSES - the dangerous expression was correctly blocked."),
        90: ("test('Compound Interest', '10000 * (1 + 0.06/4)**(4*3)', 11956.1817, tolerance=0.01)", "Tests the compound interest formula. tolerance=0.01 because we only need 2 decimal places of precision."),
        100: ("test_raises('Block __import__', \"__import__('os').system('echo hacked')\")", "Security test: verifies that attempting to import modules is blocked."),
        120: ("sys.exit(0 if failed == 0 else 1)", "Exit with code 0 (success) if all tests pass, or 1 (failure) if any test failed. This is standard for CI/CD pipelines."),
    }

    for line_num, (code, explain) in test_lines.items():
        pdf.line_explain(line_num, code, explain)

    # =====================================================================
    # CHAPTER 14: sample_doc.md
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("14. tests/sample_doc.md - Sample Test Document")

    pdf.body_text(
        "A sample Markdown document used for testing the Document RAG feature. Contains information about "
        "the Nova AI project's architecture, components, performance metrics, budget, team, and timeline. "
        "When loaded with 'load tests/sample_doc.md', this document becomes searchable - you can ask questions "
        "like 'What is the project budget?' and NOVA will retrieve and cite relevant sections."
    )

    # =====================================================================
    # CHAPTER 15: DATA FLOW
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("15. Complete Data Flow Walkthrough")

    pdf.chapter_title("Example: User asks 'What is the weather in Colombo?'", level=2)

    weather_flow = [
        "1. main.py: User types 'What is the weather in Colombo?' -> agent.process_turn() called",
        "2. agent.py: lower_input = 'what is the weather in colombo?'",
        "3. agent.py: is_greeting() -> False (not 'hi' or 'hello')",
        "4. agent.py: classify_identity_query() -> None (no identity keywords)",
        "5. agent.py: is_weather_query() -> True ('weather' matches _WEATHER_PATTERNS)",
        "6. weather.py: get_live_weather('What is the weather in Colombo?') called",
        "7. weather.py: regex strips prefix -> clean_loc = 'Colombo'",
        "8. weather.py: Strategy 1: wttr.in fetches 'Colombo: Partly cloudy +30C, Humidity: 78%'",
        "9. agent.py: build_search_augmented_prompt() wraps weather data in RAG template",
        "10. agent.py: is_rag = True (deterministic generation mode)",
        "11. memory.py: Augmented prompt added to conversation context",
        "12. llm_client.py: generate(context, is_factual_rag=True) -> greedy decoding",
        "13. agent.py: _clean_response() strips any filler from LLM output",
        "14. memory.py: Augmented prompt replaced with original user input in history",
        "15. main.py: Response displayed to user",
    ]
    for step in weather_flow:
        pdf.body_text(step)

    pdf.add_page()
    pdf.chapter_title("Example: User asks 'What is 25% of 840?'", level=2)

    math_flow = [
        "1. main.py: User types 'What is 25% of 840?' -> agent.process_turn() called",
        "2. agent.py: Not a greeting, not identity, not weather",
        "3. agent.py: No documents loaded, skip document RAG",
        "4. agent.py: is_math_query() called:",
        "   4a. Hard exclusion check: no 'president', 'who is', etc. -> passes",
        "   4b. _MATH_CANDIDATE_PATTERN: matches '25%' -> passes fast check",
        "   4c. llm.classify_math_query('What is 25% of 840?') -> LLM returns 'MATH' -> True",
        "5. math_solver.py: extract_and_solve_math() called",
        "   5a. LLM extracts expression: '0.25 * 840'",
        "   5b. _clean_expression() removes any markdown/comments",
        "   5c. safe_eval('0.25 * 840') -> AST parse -> BinOp(Mult, 0.25, 840) -> 210.0",
        "6. agent.py: build_math_narrative_prompt('What is 25% of 840?', '0.25 * 840', 210.0)",
        "   The LLM is told: 'The exact answer is 210.0. Write a step-by-step explanation.'",
        "7. LLM generates narrative around the pre-computed answer 210.0",
        "8. Response cleaned, memory updated, displayed to user",
    ]
    for step in math_flow:
        pdf.body_text(step)

    pdf.chapter_title("Example: User asks 'Who is the current president of Sri Lanka?'", level=2)

    search_flow = [
        "1. agent.py: Not greeting, not identity, not weather, not math",
        "2. agent.py: No documents loaded, skip document RAG",
        "3. agent.py: Falls through to Stage 6 (general search)",
        "4. llm_client.py: plan_search_query() -> LLM returns 'current President of Sri Lanka'",
        "5. search.py: search_and_fetch_knowledge('current President of Sri Lanka')",
        "   5a. DDGS search returns 4 results with URLs and snippets",
        "   5b. Finds Wikipedia URL -> deep scrape with CleanArticleExtractor",
        "   5c. Combines deep-scraped page + search snippets",
        "6. agent.py: build_search_augmented_prompt() wraps in injection-resistant RAG template",
        "7. LLM generates answer grounded in the search results",
        "8. _clean_response() strips fillers, memory updated with original query",
    ]
    for step in search_flow:
        pdf.body_text(step)

    # =====================================================================
    # CHAPTER 16: KEY DESIGN DECISIONS
    # =====================================================================
    pdf.add_page()
    pdf.chapter_title("16. Key Design Decisions & Patterns")

    decisions = [
        ("Why 4-bit Quantization?",
         "The Qwen 2.5 1.5B model normally needs ~3GB VRAM in float16. With NF4 4-bit quantization plus double "
         "quantization, it fits in ~1.2GB. This allows running on modest GPUs (even 4GB cards) while maintaining "
         "good quality. The quality trade-off is minimal for a 1.5B model."),
        ("Why AST-based Math Instead of eval()?",
         "Security. The LLM generates the expression, and a malicious prompt could trick it into generating "
         "dangerous code. The AST evaluator only allows arithmetic operations and whitelisted math functions. "
         "Any attempt to call system functions is blocked at the parser level."),
        ("Why Two-Stage Math Classification?",
         "A single regex would have too many false positives (e.g., 'There are 50 states in the USA' contains "
         "a number but isn't math). A pure LLM call for every query is slow and wasteful. The two-stage approach "
         "(fast regex filter + precise LLM classifier) balances speed and accuracy."),
        ("Why Replace Augmented Prompts in Memory?",
         "Lines 256-257 in agent.py remove the augmented prompt (with search results/math expressions) from "
         "memory and replace it with the original user input. This prevents the conversation history from being "
         "polluted with raw search data. The LLM would get confused if it saw '[Search Results: ...]' in previous "
         "turns."),
        ("Why Persona Drift Reminders?",
         "LLMs have limited context windows and attention mechanisms. In long conversations (20+ turns), the "
         "system prompt at position 0 gets less attention weight. Periodic reminders re-anchor the model's "
         "behavior, similar to how Claude uses <long_conversation_reminder> tags."),
        ("Why Lazy Loading for Embedding Model?",
         "The sentence-transformer model (~90MB) is only needed if the user loads documents. Loading it at "
         "startup would waste time and memory for users who never use the document RAG feature."),
        ("Why Greedy Decoding for RAG?",
         "When the response is grounded in factual data (search results, weather, math), we want maximum "
         "accuracy. Greedy decoding (do_sample=False) always picks the most probable token, reducing the "
         "risk of hallucination. For conversational responses, controlled sampling adds natural variation."),
        ("Why Custom HTML Parser Instead of BeautifulSoup?",
         "BeautifulSoup is an external dependency. Python's built-in HTMLParser is dependency-free, lighter, "
         "and sufficient for our use case. The CleanArticleExtractor specifically targets Wikipedia-style "
         "content extraction with table formatting."),
    ]

    for title, text in decisions:
        pdf.chapter_title(title, level=3)
        pdf.body_text(text)

    # =====================================================================
    # SAVE
    # =====================================================================
    output_path = os.path.join(os.path.dirname(__file__), "NOVA_AI_Project_Complete_Guide.pdf")
    pdf.output(output_path)
    print(f"\n{'='*60}")
    print(f"  PDF Generated Successfully!")
    print(f"  Location: {output_path}")
    print(f"  Pages: {pdf.page_no()}")
    print(f"{'='*60}\n")
    return output_path


if __name__ == "__main__":
    build_pdf()
