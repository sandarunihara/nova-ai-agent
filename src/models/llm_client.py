import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextStreamer
from src.utils.config import MODEL_ID, CACHE_DIR, MAX_NEW_TOKENS, TOP_P, REPETITION_PENALTY

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

    def plan_search_query(self, user_query: str) -> str:
        """
        Few-Shot Search Planner.
        Teaches Qwen-1.5B the exact boundary between search and internal reasoning.
        """
        planner_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an AI Search Planner. Your task is to output the optimal search query if external facts or new documentation are needed, "
                    "or output 'NONE' if the question can be solved with internal code debugging, math, logic, or conversation.\n\n"
                    "EXAMPLES:\n"
                    "User: Find the bug in: const user = users.find(u => u.id = 2);\n"
                    "Search Query: NONE\n\n"
                    "User: Write a python function to reverse a linked list\n"
                    "Search Query: NONE\n\n"
                    "User: Who is the current President of Sri Lanka?\n"
                    "Search Query: current President of Sri Lanka\n\n"
                    "User: What is the useActionState hook in React 19?\n"
                    "Search Query: React 19 useActionState hook documentation\n\n"
                    "User: BTC price live USD\n"
                    "Search Query: Bitcoin price USD live\n\n"
                    "User: Hello, how are you today?\n"
                    "Search Query: NONE\n\n"
                    "INSTRUCTION: Output ONLY the concise search query or 'NONE'. No explanation."
                )
            },
            {"role": "user", "content": f"User: {user_query}\nSearch Query:"}
        ]

        prompt_text = self.tokenizer.apply_chat_template(planner_prompt, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=15,
                do_sample=False,  # Strict deterministic output
                pad_token_id=self.tokenizer.pad_token_id
            )

        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        decision = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        
        # Strip quotes or leftover prefixes
        decision = decision.replace('"', '').replace("'", "").replace("Search Query:", "").strip()
        return decision

    def generate(self, messages: list, is_factual_rag: bool = False) -> str:
        prompt_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to("cuda")

        gen_kwargs = {
            "max_new_tokens": MAX_NEW_TOKENS,
            "repetition_penalty": REPETITION_PENALTY,
            "eos_token_id": self.tokenizer.eos_token_id,
            "pad_token_id": self.tokenizer.pad_token_id,
            "streamer": self.streamer
        }

        if is_factual_rag:
            gen_kwargs["do_sample"] = False  # Greedy for strict factual fidelity
        else:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = 0.3
            gen_kwargs["top_p"] = TOP_P

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
            
        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()