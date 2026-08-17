"""
src/models/llm_client.py
LLM client with Context-Aware and Topic-Shift-Aware Search Planning.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextStreamer
from src.utils.config import MODEL_ID, CACHE_DIR, MAX_NEW_TOKENS, TOP_P, REPETITION_PENALTY
from src.prompts.system_prompts import build_math_classifier_prompt

class LLMClient:
    def __init__(self):
        print(f"📦 Loading model '{MODEL_ID}' in 4-bit...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            quantization_config=bnb_config,
            cache_dir=CACHE_DIR,
            device_map="auto"
        )
        self.model.eval()
        self.streamer = TextStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

    def plan_search_query(self, user_query: str, recent_context: str = "") -> str:
        """
        Few-Shot Search Planner.
        Explicitly blocks web searches for math calculations, equations, and logic puzzles.
        """
        planner_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an AI Search Planner. Output a concise search query if live external facts, news, prices, "
                    "or framework docs are needed.\n"
                    "CRITICAL RULE: If the user query is a math calculation, algebra equation, word problem, probability question, "
                    "or financial interest formula, output EXACTLY 'NONE'. Do not search the web for math.\n\n"
                    "EXAMPLES:\n"
                    "User: If $10,000 is invested at 6% compounded quarterly for 3 years, what is the amount?\n"
                    "Search Query: NONE\n\n"
                    "User: Two trains start toward each other 600 miles apart at 60 mph and 90 mph\n"
                    "Search Query: NONE\n\n"
                    "User: A bag contains 5 red, 7 blue, and 8 green marbles. Probability both are blue?\n"
                    "Search Query: NONE\n\n"
                    "User: Who is the current President of Sri Lanka?\n"
                    "Search Query: current President of Sri Lanka\n\n"
                    "Output ONLY the concise search query or 'NONE'. No explanation."
                )
            },
            {
                "role": "user",
                "content": f"Previous Topic: {recent_context or 'None'}\nUser: {user_query}\nSearch Query:"
            }
        ]

        prompt_text = self.tokenizer.apply_chat_template(planner_prompt, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=20,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id
            )

        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        decision = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        decision = decision.replace('"', '').replace("'", "").replace("Search Query:", "").strip()

        return decision

    def generate(self, messages: list, is_factual_rag: bool = False) -> str:
        prompt_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")

        gen_kwargs = {
            "max_new_tokens": MAX_NEW_TOKENS,
            "repetition_penalty": 1.18,
            "eos_token_id": self.tokenizer.eos_token_id,
            "pad_token_id": self.tokenizer.pad_token_id,
            "streamer": self.streamer
        }

        if is_factual_rag:
            gen_kwargs["do_sample"] = False  # Deterministic greedy decoding for search facts
        else:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = 0.25
            gen_kwargs["top_p"] = TOP_P

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
            
        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    def classify_math_query(self, user_query: str) -> bool:
        """
        Uses LLM with few-shot prompt to classify whether a query is a math problem.
        Returns True if the query requires numerical computation.
        """
        messages = build_math_classifier_prompt(user_query)

        prompt_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=5,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id
            )

        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        decision = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip().upper()

        # Parse the response — look for MATH or NOT_MATH
        if "NOT_MATH" in decision:
            return False
        if "MATH" in decision:
            return True

        # Fallback: if unclear, default to False (let general reasoning handle it)
        return False