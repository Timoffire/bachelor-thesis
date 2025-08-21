from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional
import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

# ==== Deine vorhandene Pipeline ======================
# Wichtig: Stelle sicher, dass RAGPipeline und alle Imports im PYTHONPATH verfügbar sind
# oder diese Datei im selben Projekt liegt.
from rag.pipeline import RAGPipeline  # Passe den Import ggf. an

# =====================================================

logger = logging.getLogger("RAGAPI")
logging.basicConfig(level=logging.INFO)

# -------------------- Pydantic Schemas --------------------

class QueryRequest(BaseModel):
    query_text: str = Field(..., description="Suchtext für die Vektor-DB")
    n_results: int = Field(10, ge=1, le=50, description="Anzahl der zurückzugebenden Treffer")

class QueryResponse(BaseModel):
    context: str
    sources: List[str]

class IngestFolderRequest(BaseModel):
    folder_path: str = Field(..., description="Ordnerpfad mit PDFs")

class RunRequest(BaseModel):
    ticker: str = Field(..., description="Aktien-Ticker, z. B. AAPL")

class RunMetricItem(BaseModel):
    value: Any
    llm_response: str
    sources: List[str]

class RunResponse(BaseModel):
    results: Dict[str, RunMetricItem]

class HealthResponse(BaseModel):
    database: Dict[str, Any]
    llm: Dict[str, Any]

class AddDocumentRequest(BaseModel):
    path: str

# -------------------- API-Adapter-Klasse --------------------

class RAGAPI:
    """
    Dünne API-Schicht über der RAGPipeline.

    - Kapselt die RAGPipeline als Dependency
    - Bietet saubere JSON-Responses für das Frontend
    - Enthält robuste Fehlerbehandlung
    """

    def __init__(self, pipeline: Optional[RAGPipeline] = None) -> None:
        self.pipeline = pipeline or RAGPipeline()

    # ---- Endpoints ----

    def health(self) -> HealthResponse:
        try:
            status_json = self.pipeline.check_health()
            status = json.loads(status_json)
            return HealthResponse(**status)
        except Exception as e:
            logger.exception("Healthcheck fehlgeschlagen")
            raise HTTPException(status_code=500, detail=f"Healthcheck fehlgeschlagen: {e}")

    def ingest_folder(self, payload: IngestFolderRequest) -> dict:
        try:
            if not os.path.isdir(payload.folder_path):
                raise HTTPException(status_code=400, detail="Ordner nicht gefunden oder kein Verzeichnis")
            self.pipeline.ingest_pdf_folder(payload.folder_path)
            return {"message": "Ingestion gestartet/abgeschlossen", "folder": payload.folder_path}
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Fehler bei ingest_folder")
            raise HTTPException(status_code=500, detail=str(e))

    def add_document(self, path: str) -> dict:
        try:
            if not os.path.isfile(path):
                raise HTTPException(status_code=400, detail="Datei nicht gefunden")
            if not path.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Nur PDF-Dateien werden akzeptiert")

            self.pipeline.add_document(path)
            return {"message": "Dokument hinzugefügt", "path": path}
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Fehler bei add_document")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_collection(self) -> dict:
        try:
            self.pipeline.delete_collection()
            return {"message": "Collection gelöscht"}
        except Exception as e:
            logger.exception("Fehler bei delete_collection")
            raise HTTPException(status_code=500, detail=str(e))

    def query(self, payload: QueryRequest) -> QueryResponse:
        try:
            context, sources = self.pipeline.query(payload.query_text, n_results=payload.n_results)
            return QueryResponse(context=context, sources=sources)
        except Exception as e:
            logger.exception("Fehler bei query")
            raise HTTPException(status_code=500, detail=str(e))

    def run(self, payload: RunRequest) -> RunResponse:
        try:
            raw = self.pipeline.run(payload.ticker)
            # Rohformat -> pydantic-konformes Mapping
            normalized: Dict[str, RunMetricItem] = {}
            for metric, content in raw.items():
                normalized[metric] = RunMetricItem(
                    value=content.get("value"),
                    llm_response=content.get("llm_response", ""),
                    sources=content.get("sources", []),
                )
            return RunResponse(results=normalized)
        except Exception as e:
            logger.exception("Fehler bei run")
            raise HTTPException(status_code=500, detail=str(e))

# -------------------- FastAPI-Wiring --------------------

router = APIRouter()

# Dependency, damit die Pipeline leicht mock-/austauschbar ist

def get_api() -> RAGAPI:
    return RAGAPI()

@router.get("/health", response_model=HealthResponse)
def health(api: RAGAPI = Depends(get_api)):
    return api.health()

@router.post("/ingest-folder")
def ingest_folder(payload: IngestFolderRequest, api: RAGAPI = Depends(get_api)):
    return api.ingest_folder(payload)

@router.post("/add-document")
def add_document(payload: AddDocumentRequest, api: RAGAPI = Depends(get_api)):
    return api.add_document(payload.path)

@router.delete("/collection")
def delete_collection(api: RAGAPI = Depends(get_api)):
    return api.delete_collection()

@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, api: RAGAPI = Depends(get_api)):
    return api.query(payload)

@router.post("/run", response_model=RunResponse)
def run(payload: RunRequest, api: RAGAPI = Depends(get_api)):
    return api.run(payload)


def build_app() -> FastAPI:
    app = FastAPI(title="RAGPipeline API", version="1.0.0")

    # CORS für Frontends (anpassen für Produktion)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    return app


app = build_app()

# ---- Lokaler Start: uvicorn fastapi_rag_api:app --reload ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_rag_api:app", host="0.0.0.0", port=8000, reload=True)
