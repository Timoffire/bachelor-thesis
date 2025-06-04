# Backend Dokumentation

Dieses Backend stellt eine RAG-Pipeline bereit, die beliebige PDF-Dokumente ingestiert, relevante Kontextabschnitte für Anfragen abruft und mithilfe eines LLMs strukturierte Analysen zu Finanzkennzahlen erstellt.

## Features

### 1. Ingestion (Dokumentenverarbeitung)
- `RAGPipeline.ingest_pdf_folder(folder_path: str)`
  - Lädt alle PDF-Dateien eines Ordners in eine lokale ChromaDB (Vector Database).
  - Extrahiert Text mittels `pdfplumber` und berechnet Embeddings.

### 2. Retrieval (Kontextabruf)
- `RAGPipeline.retrieve_context(query: str, n_results: int = 3)`
  - Führt eine Ähnlichkeitssuche in ChromaDB durch.
  - Gibt den relevanten Text-Snippet (`context`) und eine Liste von Quellenpfaden zurück.

### 3. Analysen (Prompt & LLM)
- `RAGPipeline.run(ticker: str, metrics: list, embedding_model: str = None, llm_model: str = None) -> dict`
  - Ruft Finanzkennzahlen für einen gegebenen `ticker` via API auf (`get_stock_metrics`).
  - Baut für jede Metrik mithilfe von `build_prompt` einen Prompt und sendet ihn an das LLM.
  - Modelle lassen sich dynamisch wählen (Standard: `text-embedding-ada-002`, `gpt-3.5-turbo`).
  - Rückgabe: Struktur mit `result` (Antwort-Texte) und `sources` (Liste der genutzten Dokumentenpfade).

## API Endpoints

### GET /health
- **Antwort:** `{ "status": "ok" }`

### POST /analyze
- **Request Body:**
  ```json
  {
    "ticker": "AAPL",
    "metrics": ["pe_ratio", "market_cap"],
    "embedding_model": "text-embedding-ada-002",    # optional
    "llm_model": "gpt-4"                          # optional
  }
  ```
- **Response:**
  ```json
  {
    "result": {
      "result": ["Analyse zu Metrik1...", "Analyse zu Metrik2..."],
      "sources": [["/path/doc1.pdf"], ["/path/doc2.pdf"]]
    }
  }
  ```

## Environment Variables
- `OPENAI_API_KEY`: API-Key für OpenAI (Embedding & LLM Zugriff)

## Dependencies
- `fastapi`, `uvicorn`, `pdfplumber`, `chromadb`, `pydantic`, `python-dotenv`

## Running
- Beispiel: `uvicorn main:app --reload`
