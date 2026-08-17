# Nova AI Project — Technical Design Document

## Architecture Overview

Nova AI is a modular personal assistant built for Sandaru Nihara. The system uses a Qwen 2.5 1.5B Instruct model running locally with 4-bit quantization via BitsAndBytes. The architecture follows a pipeline pattern where user input flows through multiple routing stages.

## Core Components

### 1. Agent Router
The agent router is the central orchestrator. It classifies incoming queries into categories:
- **Greetings**: Simple hello/hi patterns
- **Identity Queries**: Questions about who Nova is, who the user is, or who created Nova
- **Weather**: Live weather data retrieval
- **Document RAG**: Searching loaded PDF and Markdown files
- **Math Problems**: Numerical computation with AST-safe evaluation
- **Web Search**: General knowledge retrieval via DuckDuckGo

### 2. LLM Client
The LLM client wraps the Qwen 2.5 model with HuggingFace Transformers. It provides:
- `generate()`: Main text generation with streaming output
- `plan_search_query()`: Decides if a web search is needed
- `classify_math_query()`: Few-shot LLM classification for math detection

### 3. Math Solver
The math solver uses a two-stage approach:
1. **Expression Extraction**: The LLM converts word problems into Python expressions
2. **Safe Evaluation**: An AST-based evaluator computes the result without using eval()

Supported operations include arithmetic, math.sqrt, math.sin, math.cos, math.tan, math.log, math.factorial, math.comb, and math.perm.

### 4. Memory System
Conversation memory stores the last 10 turns with periodic persona drift reminders every 4 turns.

## Performance Metrics

The system runs on a single GPU with approximately 1.2GB VRAM usage for the quantized model. Average response latency is 2-4 seconds depending on output length. The embedding model for document RAG uses approximately 90MB of RAM.

## Budget Allocation

The total project budget is $15,000 allocated as follows:
- Hardware (GPU server): $8,000
- Software licenses: $2,000
- Development time: $3,500
- Testing and QA: $1,500

## Team Members

The development team consists of:
- Sandaru Nihara — Lead Developer and Project Owner
- The project is a solo endeavor with AI assistance

## Timeline

Phase 1 (Complete): Core chat functionality with persona
Phase 2 (Complete): Web search integration
Phase 3 (Complete): Math solver with safe evaluation
Phase 4 (Current): Document RAG for PDF and Markdown files
Phase 5 (Planned): Voice interface integration
