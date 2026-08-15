import os

# Storage and Cache on Drive E
os.environ["HF_HOME"] = "E:/huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
CACHE_DIR = "E:/huggingface_cache"

# Generation Hyperparameters
MAX_NEW_TOKENS = 350
TEMPERATURE = 0.2
TOP_P = 0.85
REPETITION_PENALTY = 1.15
MAX_HISTORY_TURNS = 6