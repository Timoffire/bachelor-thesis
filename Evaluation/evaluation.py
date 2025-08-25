import os
from Backend.rag.vectordb import ChromaDBConnector
from Backend.rag.llm import call_llm
import pandas as pd
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
def _sanitize_for_path(name: str) -> str:
    """Ersetzt problematische Zeichen für Dateisystem-Pfade."""
    return "".join(c if c.isalnum() or c in ('-', '_') else '-' for c in name)

class Evaluation:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "docs",
                 embedding_model: str = "mxbai-embed-large", llm_model: str = "llama3"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.db_connector = ChromaDBConnector(
            path=self.persist_directory,
            embedding_model=self.embedding_model
        )
        self.csv_path = "QA/questions.csv"
    def query(self, query_text: str, n_results: int = 5):
        results = self.db_connector.query_collection(query_text,n_results)

        context_parts = []

        for doc_id, doc_text in results:
            # Nur den Dokument-Text zum Kontext hinzufügen (ohne Quellenangabe)
            context_parts.append(doc_text)

        # Gesamten Kontext zusammenfügen
        context = "\n\n".join(context_parts)

        return context

    def prompt_builder(self, question: str, context: str) -> str:
        """
        Baut einen Prompt:
        - Mit Kontext: Antwort nur aus Kontext, sonst "Unknown".
        - Ohne Kontext: Nur antworten, wenn sicher, sonst "Unknown".
        Format: immer mit "Verdict: ..." beginnen.
        """
        if context and context.strip():
            # Mit Kontext
            return (
                "You are a corporate finance analyst. Answer in English.\n"
                "Note: The provided context may be incomplete, generic, or irrelevant.\n"
                "Rules:\n"
                "1) First, critically check if the context contains directly relevant and specific information for the question.\n"
                "2) Use the context ONLY if it clearly and unambiguously supports 'For' or 'Against'.\n"
                "3) Do not speculate, infer, or assume anything beyond the explicit content of the context.\n"
                "4) Always start with one of: Verdict: For or Verdict: Against.\n"
                "5) After the verdict, add a very short justification (1–2 sentences, max 40 words).\n\n"
                f"Context:\n{context}\n\n"
                f"Question:\n{question}\n"
            )
        else:
            # Ohne Kontext
            return (
                "You are a corporate finance analyst. Answer in English.\n"
                "Rules:\n"
                "1) Base your answer ONLY on universally accepted and undisputed corporate finance principles.\n"
                "2) You must be 100% certain, with zero doubt, before giving 'For' or 'Against'.\n"
                "3) Never speculate, never assume missing facts, and never rely on probability.\n"
                "4) Always start with one of: Verdict: For or Verdict: Against.\n"
                "5) After the verdict, add a very short justification (1–2 sentences, max 40 words).\n\n"
                f"Question:\n{question}\n"
            )

    def add_pdf_to_db(self, path: str):
        """
        Fügt eine PDF-Datei zur ChromaDB hinzu.
        """
        for filename in os.listdir(path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(path, filename)
                self.db_connector.add_pdf_to_collection(pdf_path= pdf_path)

    def add_single_pdf(self, path: str):
        self.db_connector.add_pdf_to_collection(pdf_path=path)

    def evaluate(self, models=None, temperature: float = 0.0, out_dir: str = "Results"):
        # Fallback-Modelle (als Liste, nicht als ein einzelner String)
        if models is None:
            models = ["mistral:7b"]
        # Falls der Aufrufer versehentlich einen String übergibt -> in Liste umwandeln
        if isinstance(models, str):
            # Unterstützung für "comma separated"
            models = [m.strip() for m in models.split(",") if m.strip()]

        os.makedirs(out_dir, exist_ok=True)

        df = pd.read_csv(self.csv_path, encoding="utf-8", delimiter=";")
        questions = df["question"].tolist()

        REPEATS = 5  # Anzahl der Wiederholungen pro Modell

        for model in models:
            model_safe = _sanitize_for_path(model)
            model_dir = os.path.join(out_dir, model_safe)
            os.makedirs(model_dir, exist_ok=True)

            for run_idx in range(1, REPEATS + 1):
                rows = []

                for i, question in enumerate(questions, start=1):
                    context = self.query(question)
                    logging.info(f"[{model} | Run {run_idx}] Retrieved context for question {i}: {context[:100]}...")
                    context_prompt = self.prompt_builder(question, context)
                    no_context_prompt = self.prompt_builder(question, "")

                    logging.info(f"[{model} | Run {run_idx}] Evaluating question {i}: {question}")

                    answer_context = call_llm(
                        prompt=context_prompt, model_name=model, temperature=temperature
                    )
                    answer_no_context = call_llm(
                        prompt=no_context_prompt, model_name=model, temperature=temperature
                    )

                    rows.append({
                        "model": model,
                        "run": run_idx,
                        "question_number": i,
                        "question": question,
                        "answer_context": answer_context,
                        "answer_no_context": answer_no_context,
                    })

                # gewünschte Spaltenreihenfolge
                out_df = pd.DataFrame(
                    rows,
                    columns=["model", "run", "question_number", "question", "answer_context", "answer_no_context"]
                )
                out_path = os.path.join(model_dir, f"answers_run{run_idx}_{model_safe}.csv")
                out_df.to_csv(out_path, index=False, encoding="utf-8")

        return None

if __name__ == "__main__":
    logging.info("Starting Evaluation")
    evaluator = Evaluation()
    evaluator.evaluate()