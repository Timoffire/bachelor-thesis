# 📈 Context-Aware RAG for **Interpretable Stock Analysis**

> **Bachelor Thesis:** *Developing a Context-Aware RAG-System for Interpretable Stock Analysis Using Financial Literature*

<div align="center">

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Frontend](https://img.shields.io/badge/frontend-Next.js%2015.5.0-black)
![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20Python%203.9-blue)
![License](https://img.shields.io/badge/license-Academic-lightgrey)

</div>

## 🚀 Project Name & One-liner

A **RAG-powered** analysis tool that ingests financial literature to explain a stock’s **fundamental metrics** in an **interpretable** way.
Built for students, analysts, and researchers who need **transparent** LLM rationales tied to sources.

---

## ✨ Features

* ✅ **Upload financial literature** (reports, PDFs, papers)
* ✅ **RAG + LLM** analysis of a stock via **fundamental metrics**
* ✅ **Interpretable explanations** with cited context per metric
* ✅ **Frontend flow**: Landing → Analysis → Metric detail
* ✅ **Reset & Re-run** (reset collection, start new runs)

---

## 🗂 Project Structure (short overview)

```text
.
├── Backend
│   ├── fastapi_rag_api.py           # FastAPI entrypoint (Uvicorn)
│   └── rag
│       ├── __init__.py
│       ├── llm.py                   # LLM provider & call wrapper
│       ├── metrics.py               # Metrics Retriever
│       ├── pipeline.py              # End-to-end RAG pipeline
│       ├── prompt_engineering.py    # Prompts generator
│       ├── query_builder.py         # Query construction for RAG
│       └── vectordb.py              # ChromaDB interface
├── Evaluation
│   ├── Literature                   # Literature for RAG
│   ├── QA                           # Q/A for benchmarking
│   ├── Results                      # Model comparisons
│   │   ├── gemma-7b
│   │   ├── llama2-7b
│   │   ├── llama3-latest
│   │   └── mistral-7b
│   ├── chroma_db                    # Eval DB
│   └── evaluation.py                # Evaluation script
├── frontend
│   ├── public
│   │   └── Literature               # User Uploads
│   ├── src
│   │   ├── app
│   │   │   ├── api                  # Next.js Route Handlers
│   │   │   │   ├── last-run
│   │   │   │   ├── reset-collection
│   │   │   │   ├── run
│   │   │   │   ├── submit-literature
│   │   │   │   └── upload-literature
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── results
│   │   │       ├── [metric]
│   │   │       │   ├── loading.tsx
│   │   │       │   ├── not-found.tsx
│   │   │       │   └── page.tsx
│   │   │       ├── layout.tsx
│   │   │       └── page.tsx
│   │   ├── components
│   │   │   ├── GradientButton.tsx
│   │   │   ├── MetricCard.tsx
│   │   │   ├── MetricsGrid8.tsx
│   │   │   ├── TextWindow.tsx
│   │   │   └── ui
│   │   │       ├── CenterFooter.tsx
│   │   │       └── CopyButton.tsx
```

---

## 🔧 Prerequisites

**System / Runtime**

* **Frontend:** Node.js **≥ 18** (recommend: 20 LTS), **Next.js 15.5.0**
* **Backend:** **Python 3.9**, `uvicorn`, `fastapi`
* **Tools:** Git, (optional) `make`, (optional) `pnpm`/`npm`

**Package managers**

* Frontend: `pnpm` **or** `npm`
* Backend: `pip` (virtual env via `venv`)

---

## 📦 Installation

### 1) Backend (FastAPI)

```bash
python3.9 -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install --upgrade pip
# If a requirements.txt exists:
pip install -r requirements.txt
````

---

### 2) Frontend (Next.js 15.5.0)

```bash
cd frontend
npm install           # or: npm install
```

---

### 3) Ollama Models

For the application to work, the following models must be downloaded in Ollama:

```bash
ollama pull llama3:latest
ollama pull mxbai-embed-large:latest
```

---

## 🏃 Quickstart

> Open **two terminals**—one for the backend, one for the frontend.

**Terminal 1 — start Backend**

```bash
cd Backend
source .venv/bin/activate                  # Windows: .venv\Scripts\Activate.ps1
uvicorn fastapi_rag_api:app --reload --port 8000
````

**Terminal 2 — start Frontend**

```bash
cd frontend
npm run dev                                   # or: pnpm dev
# App runs on http://localhost:3000
```

---

⚠️ **Note:** Make sure the **Ollama service is running** before starting the backend.
For example, you can start it with:

```bash
ollama serve
```

**Expected endpoints (examples)**

* `POST /run` — start an analysis for a ticker (used by `src/app/api/run`)
* `POST /upload-literature` — upload financial documents
* `POST /reset-collection` — reset the collection
* `GET  /last-run` — status / last results

*(Next.js Route Handlers under `src/app/api/*` proxy requests to the FastAPI backend.)*

---

## 🖱️ Usage (typical workflows)

### 1) **Landing page**

* 📤 **Upload documents:** feed financial Literature PDFs into the vector DB (ideally fundamental analytical)
* ♻️ **Reset collection** when needed
* ▶️ **Start analysis:** enter ticker (e.g., `AAPL`) → **Run**

### 2) **Analysis page**

* 📊 See **all fundamental metrics** incl. current values
* 🔍 Click a metric to open the **Metric page**

### 3) **Metric page**

* 🧠 **LLM explanation** for the **selected metric**, grounded with RAG sources

---

## 🧪 Evaluation (brief)

* **Datasets:** `Evaluation/Literature`, `Evaluation/QA`
* **Results:** `Evaluation/Results/*` for models (`gemma-7b`, `llama2-7b`, `llama3-latest`, `mistral-7b`)
* **Script:** `Evaluation/evaluation.py` to reproduce/update outcomes


---

## 🧯 Troubleshooting

<details>
<summary><b>Frontend cannot reach Backend</b></summary>

* Confirm backend is running at <code>[http://localhost:8000](http://localhost:8000)</code>.
* CORS: does <code>ALLOWED\_ORIGINS</code> include the frontend URL?
* Check Route Handler base URL / frontend env.

</details>

<details>
<summary><b>Uploads don’t appear in analysis</b></summary>

* Did you **Run** after uploading?
* Are files in the expected path (`public/Literature` or via upload endpoint)?
* Check `CHROMA_DB_DIR` and write permissions.

</details>

<details>
<summary><b>LLM errors / rate limits</b></summary>

* Is Ollama running?
* Verify model/provider settings in `rag/llm.py`.
* Tune retry/timeouts in the pipeline if needed.

</details>

---

## 📜 License

**Academic use only** within the bachelor thesis scope. For other use, please request permission first.

