import os
from Backend.rag.vectordb import ChromaDBConnector
from Backend.rag.llm import call_llm
import pandas as pd
import logging
import time
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class Evaluation:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "docs",
                 embedding_model: str = "nomic-embed-text", llm_model: str = "llama3"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.db_connector = ChromaDBConnector(
            path=self.persist_directory,
            embedding_model=self.embedding_model
        )
        self.csv_path = "QA/questions.csv"
    def query(self, query_text: str, n_results: int = 10):
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
        Erzeugt einen *einheitlichen* Prompt für Finanzfragen.
        Der Prompt ist in beiden Modi gleich – es wird lediglich optional ein 'Context:'-Block eingefügt.
        """
        if context == "":
            context = None
        base = (
            "You are a concise finance analyst. Answer in English.\n"
            "Task: Provide a very short, decision-oriented assessment of the question below.\n"
            "Format strictly as:\n"
            "Verdict: For or Against\n"
            "Why: one or two short sentences, plain language.\n"
            "Guidelines: Use basic financial reasoning. "
            "Avoid speculation, avoid jargon, no more than ~40 words total.\n\n"
        )

        ctx_block = f"Context:\n{context}\n\n" if context and context.strip() else ""
        prompt = (
            f"{base}"
            f"{ctx_block}"
            f"Question:\n{question}\n"
        )
        return prompt
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


    def evaluate(self, models=None, temperature=0.1, out_dir="Results"):
        if models is None:
            models = ["llama3:latest", "llama2:7b", "mistral:7b", "gemma:7b"]

        os.makedirs(out_dir, exist_ok=True)

        df = pd.read_csv(self.csv_path, encoding="utf-8", delimiter=";")
        questions = df["question"].tolist()

        all_rows = []

        for model in models:
            model_rows = []
            for question in questions:
                context = self.query(question)
                context_prompt = self.prompt_builder(question, context)
                no_context_prompt = self.prompt_builder(question, "")
                logging.info(f"Evaluating model: {model} with question: {question}")
                answer_context = call_llm(prompt=context_prompt, model_name=model, temperature=temperature)
                answer_no_context = call_llm(prompt=no_context_prompt, model_name=model, temperature=temperature)
                row = {
                    "model": model,
                    "question": question,
                    "answer_context": answer_context,
                    "answer_no_context": answer_no_context,
                }
                all_rows.append(row)
                model_rows.append(row)

            # pro Modell separate Datei
            pd.DataFrame(model_rows).to_csv(
                os.path.join(out_dir, f"answers_{model.replace(':','-')}.csv"),
                index=False,
                encoding="utf-8"
            )

        # alle Modelle gemeinsam
        answer_df = pd.DataFrame(all_rows)
        answer_df.to_csv(os.path.join(out_dir, "answers_all_models.csv"), index=False, encoding="utf-8")
        return answer_df

if __name__ == "__main__":
    logging.info("Starting Evaluation")
    evaluator = Evaluation()
    df = evaluator.evaluate()