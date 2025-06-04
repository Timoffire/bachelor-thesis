from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from rag.pipeline import RAGPipeline

app = FastAPI()

# CORS für Next.js (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()

class AnalysisRequest(BaseModel):
    ticker: str
    metrics: List[str]
    embedding_model: Optional[str] = None
    llm_model: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: AnalysisRequest):
    """
    Empfängt Aktienticker & Metriken vom Frontend und gibt Analyse zurück.
    """
    try:
        result, sources = pipeline.run(request.ticker, request.metrics, embedding_model=request.embedding_model, llm_model=request.llm_model)
        return {"result": result, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_document")
def add_document(request: AnalysisRequest):
    """
    Fügt der lokalen ChromaDB VectorDB ein PDF-Dokument hinzu.
    """
    try:
        pipeline.add_document(request.pdf_path, collection_name=request.collection_name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Settings for the backend you request from the frontend
@app.get("/settings")
def settings():
    #change ollama base url
    
    #change embedding model

    #change llm model

    #change collection name

    #change persist directory

    #change top_k

    return {"status": "ok"}

    
