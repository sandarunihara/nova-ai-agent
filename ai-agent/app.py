"""
app.py
FastAPI Backend Server for NOVA AI Assistant & RAG Engine.
"""

import os
import shutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent.agent import NovaAgent

# Create a global dictionary to hold our agent safely
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs exactly ONCE when the server starts up
    print("🚀 Booting up NOVA Agent and allocating GPU memory...")
    ml_models["agent"] = NovaAgent()
    print("✅ NOVA Agent is ready to serve.")
    yield
    # This runs when the server shuts down
    print("🛑 Shutting down NOVA Agent...")
    ml_models.clear()

app = FastAPI(title="NOVA AI Backend", version="2.0", lifespan=lifespan)

# Enable CORS for React frontend (localhost:3000 or localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary upload directory
UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    mode: str = "agent"  # "agent" (AI Chat + RAG) or "pure_rag" (Strict document Q&A)

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    agent = ml_models.get("agent")
    if not agent:
        raise HTTPException(status_code=503, detail="Agent is still loading.")
        
    try:
        if req.mode == "pure_rag":
            if not agent.doc_store.has_documents:
                return {"response": "No documents are currently loaded, Sir. Please upload a file first."}
            
            doc_result = agent._try_document_search(req.message)
            if doc_result:
                doc_context, source_info, _ = doc_result
                from src.prompts.system_prompts import build_document_rag_prompt
                prompt = build_document_rag_prompt(req.message, doc_context, source_info)
                response = agent.llm.generate(
                    [{"role": "system", "content": agent.memory.messages[0]["content"]}, 
                     {"role": "user", "content": prompt}], 
                    is_factual_rag=True
                )
                return {"response": agent._clean_response(response)}
            else:
                return {"response": "The loaded documents do not contain information regarding your query, Sir."}

        # Default AI Chat Agent Mode
        response = agent.process_turn(req.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    agent = ml_models.get("agent")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = agent.doc_store.load_document(file_path)
        if result["success"]:
            return {"status": "success", "filename": result["doc_name"], "chunks": result["chunks"]}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/docs")
async def list_docs():
    agent = ml_models.get("agent")
    return {"documents": agent.doc_store.list_documents()}

@app.post("/api/clear")
async def clear_memory():
    agent = ml_models.get("agent")
    if agent:
        agent.memory.reset()
    return {"status": "success", "message": "Memory cleared"}

if __name__ == "__main__":
    import uvicorn
    # IMPORTANT: reload=False prevents Windows from spawning duplicate GPU processes
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)