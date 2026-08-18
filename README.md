# ✨ NOVA AI Agent System

> **A Modular Autonomous AI Assistant & RAG Engine**  
> Powered by **Qwen 2.5 1.5B Instruct** (4-bit BitsAndBytes Quantization), **FastAPI**, **React + Vite**, and **PyTorch CUDA**.

---

## 📌 Overview

**NOVA** is a modular, high-performance personal AI agent engineered for local execution with minimal VRAM overhead (~1.2 GB VRAM). NOVA goes beyond traditional chatbots by serving as an intelligent query orchestrator. It automatically routes incoming queries through specialized intent classifiers and execution engines—including real-time web retrieval, document RAG (PDF & Markdown), AST-safe math evaluation, live weather lookup, and long-conversation persona stabilization.

The system features both a **modern React Web UI** and a **dedicated CLI Terminal interface**, powered by a high-throughput **FastAPI backend REST server**.

---

## 🚀 Key Features & Capabilities

- 🤖 **Local LLM Engine**: Runs `Qwen/Qwen2.5-1.5B-Instruct` using 4-bit NormalFloat4 (NF4) quantization via `bitsandbytes`, making GPU memory consumption extremely lightweight (~1.2 GB VRAM).
- 🌐 **Web Search RAG**: Integrated 2-stage Retrieval-Augmented Generation pipeline using DuckDuckGo search (`ddgs`) and a custom HTML article extractor that parses tables and structured records while stripping web clutter and infoboxes.
- 📄 **Document RAG Engine**: Load, index, and query PDF documents (`PyMuPDF`) and Markdown files locally. Uses `sentence-transformers/all-MiniLM-L6-v2` for high-precision semantic search and vector retrieval.
- 🧮 **AST-Safe Math Engine**: Translates natural language math word problems into clean Python mathematical expressions, evaluated safely using Python's Abstract Syntax Tree (`ast`) parser without dangerous `eval()` execution.
- 🌤️ **Live Meteorological Engine**: Real-time live weather lookup via `wttr.in` and `Open-Meteo` APIs requiring **zero API keys**.
- 🧠 **Persona Drift Prevention**: Injects periodic persona stabilization anchors into the context window during multi-turn conversations to prevent identity loss.
- 🎨 **Modern React Web Interface**: Dark-themed, responsive dashboard built with React 19, Vite, Lucide Icons, KaTeX LaTeX renderer, and React Syntax Highlighter for smooth UI interactions.
- 📑 **Project Guide PDF Generator**: Includes `generate_project_guide.py` to auto-generate a comprehensive line-by-line architectural guide in PDF format.

---

## 🏗️ System Architecture

```
                      +----------------------------------+
                      |    Client Interface Layer        |
                      |  (React Web UI / CLI Terminal)   |
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------------------------+
                      |   FastAPI REST Backend Server    |
                      |          (app.py)                |
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------------------------+
                      |        NovaAgent Router          |
                      |       (src/agent/agent.py)       |
                      +---+--------+--------+--------+---+
                          |        |        |        |
        +-----------------+        |        |        +-----------------+
        |                          |        |                          |
        v                          v        v                          v
+---------------+    +-----------------+  +---------------+    +---------------+
| Web Search    |    | Document RAG    |  | Math Solver   |    | Weather Tool  |
| DDGS + Scrape |    | MiniLM + Vector |  | LLM + AST     |    | wttr.in/Meteo |
+---------------+    +-----------------+  +---------------+    +---------------+
        |                          |        |                          |
        +-----------------+        |        |        +-----------------+
                          |        |        |        |
                          v        v        v        v
                      +----------------------------------+
                      |  Qwen 2.5 1.5B LLM (4-bit NF4)   |
                      |      Response Synthesis          |
                      +----------------------------------+
```

---

## 💻 Tech Stack & Requirements

### Tech Stack
- **Backend**: Python 3.10+, FastAPI, Uvicorn, PyTorch (CUDA), Transformers, BitsAndBytes, Sentence-Transformers, PyMuPDF.
- **Frontend**: React 19, Vite, Lucide React, React Markdown, KaTeX, Rehype-KaTeX, Remark-Math.
- **Data & Model Cache**: Defaulted to `E:/huggingface_cache` (configurable in `config.py`).

### Hardware Requirements
- **GPU**: NVIDIA GPU with CUDA support (Minimum 4 GB VRAM recommended; runs comfortably on GTX 1650 / RTX 2060 or higher).
- **RAM**: 8 GB minimum (16 GB recommended).
- **Disk Space**: ~4 GB for model weights and cache storage.

---

## 📥 Prerequisites

Before setting up the project, ensure you have installed:
1. **Python 3.10+** (Verify with `python --version`)
2. **Node.js 18+** & **npm** (Verify with `node -v` and `npm -v`)
3. **NVIDIA CUDA Toolkit** (Compatible with PyTorch PyTorch 2.x CUDA 11.8 or 12.1)

---

## 🛠️ Step-by-Step Installation & Setup

### Step 1: Open Terminal in Project Root
```powershell
cd "e:\Work\Own Projects\Python\NOVA"
```

---

### Step 2: Backend Setup (`ai-agent`)

1. **Navigate to the backend directory**:
   ```powershell
   cd ai-agent
   ```

2. **Create a Python Virtual Environment**:
   ```powershell
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```

4. **Install PyTorch with CUDA Support**:
   *(Ensure PyTorch is installed with CUDA support for GPU acceleration)*:
   ```powershell
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

5. **Install Required Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

6. **Verify CUDA Availability**:
   ```powershell
   python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
   ```

---

### Step 3: Frontend Setup (`novaui`)

1. **Open a new terminal window/tab** and navigate to the `novaui` directory:
   ```powershell
   cd "e:\Work\Own Projects\Python\NOVA\novaui"
   ```

2. **Install Node Package Dependencies**:
   ```powershell
   npm install
   ```

---

## 🚦 How to Run the Full System

### Option A: Launch Web System (Backend REST API + React UI)

1. **Start the FastAPI Backend Server**:
   In the `ai-agent` directory (with virtual environment activated):
   ```powershell
   python app.py
   ```
   *The server will initialize the GPU, load Qwen 2.5 1.5B, and start listening on `http://127.0.0.1:8000`.*

2. **Start the React Frontend Development Server**:
   In the `novaui` directory:
   ```powershell
   npm run dev
   ```
   *Open your browser and navigate to `http://localhost:5173`.*

---

### Option B: Launch Interactive CLI Assistant

If you prefer using NOVA in terminal mode without running the web server:

1. Navigate to `ai-agent` and activate the virtual environment.
2. Run `main.py`:
   ```powershell
   python main.py
   ```
3. Interactive CLI commands available inside NOVA prompt:
   - `load <filepath>` : Load a PDF or Markdown document into the RAG vector store.
   - `docs` : List all loaded documents and chunk stats.
   - `unload <name>` : Unload a document from memory.
   - `clear` : Reset conversation history.
   - `exit` : Power down NOVA.

---

### Option C: Generate Architectural Project Guide (PDF)

To generate the complete line-by-line documentation PDF:

```powershell
cd ai-agent
python generate_project_guide.py
```
*Creates `NOVA_AI_Agent_Project_Guide.pdf` in the `ai-agent` folder.*

---

## 🔌 API Endpoint Documentation

The FastAPI backend exposes the following REST endpoints on `http://127.0.0.1:8000`:

| Endpoint | Method | Description | Request Body / Params |
|---|---|---|---|
| `/api/chat` | `POST` | Process user query through NOVA Agent or Pure RAG | `{"message": "string", "mode": "agent" \| "pure_rag"}` |
| `/api/upload` | `POST` | Upload PDF or Markdown document for local RAG | `file`: Form-Data UploadFile |
| `/api/docs` | `GET` | List all currently indexed documents in vector store | *None* |
| `/api/clear` | `POST` | Reset conversation memory | *None* |

---

## 📂 Project Directory Structure

```
NOVA/
├── README.md                      # Complete System Setup & Documentation
├── ai-agent/                      # FastAPI Backend & Agent Core
│   ├── .env                       # Environment variables
│   ├── app.py                     # FastAPI REST Server
│   ├── main.py                    # Interactive CLI Interface
│   ├── generate_project_guide.py  # PDF Documentation Generator
│   ├── requirements.txt           # Python Package Dependencies
│   ├── uploaded_docs/             # Staging folder for uploaded RAG documents
│   └── src/
│       ├── agent/
│       │   ├── agent.py           # Core Agent Orchestrator & Query Router
│       │   └── memory.py          # Chat History & Persona Stabilization
│       ├── models/
│       │   └── llm_client.py      # LLM Loading, Quantization, Generation & Planner
│       ├── prompts/
│       │   └── system_prompts.py  # System Prompts & Intent Prompts
│       ├── tools/
│       │   ├── document_rag.py    # Local Vector RAG (PyMuPDF + MiniLM)
│       │   ├── math_solver.py     # AST-Safe Python Math Evaluator
│       │   ├── search.py          # Web Search (DDGS) + Deep Article Scraper
│       │   └── weather.py         # Live Weather Lookup (wttr.in + Open-Meteo)
│       └── utils/
│           └── config.py          # Central Hyperparameters & Cache Paths
└── novaui/                        # React + Vite Web UI
    ├── index.html                 # App HTML Entry
    ├── package.json               # Node Dependencies & Scripts
    ├── vite.config.js             # Vite Configuration
    └── src/                       # React Components & Styling
```

---

## ❓ Troubleshooting & FAQs

### 1. `CUDA out of memory` Error
- Check that no other process is utilizing your GPU VRAM.
- Ensure `BitsAndBytesConfig` load_in_4bit is enabled in `src/models/llm_client.py`.
- Lower `MAX_NEW_TOKENS` in `src/utils/config.py` if running on sub-4GB VRAM cards.

### 2. Changing HuggingFace Model Cache Location
By default, model weights download to `E:/huggingface_cache`. To change this path:
Modify `HF_HOME` and `CACHE_DIR` in `ai-agent/src/utils/config.py`:
```python
os.environ["HF_HOME"] = "C:/your_custom_path/huggingface_cache"
CACHE_DIR = "C:/your_custom_path/huggingface_cache"
```

### 3. CORS Error between Frontend and Backend
Ensure FastAPI backend server is running on `http://127.0.0.1:8000`. The CORS middleware in `app.py` is configured to accept requests from any origin (`allow_origins=["*"]`).

---

## 📄 License & Attribution

Developed by **Sandaru Nihara** for the NOVA AI Assistant Project.  
Powered by **Qwen LLM** (Alibaba Cloud) and HuggingFace Transformers.
