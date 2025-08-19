import os
from Backend.rag.vectordb import ChromaDBConnector
from Backend.rag.llm import call_llm
import pandas as pd
import logging
csv_path = "Evaluation/QA/questions.csv"

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
                self.db_connector.add_pdf_to_collection(pdf_path)

    def evaluate(self):

        df = pd.read_csv(csv_path)
        questions = questions = df['question'].tolist()

        #run llm with context
        answers = []
        for question in questions:
            context = self.query(question)
            context_prompt = self.prompt_builder(question, context)
            no_context_prompt = self.prompt_builder(question, "")
            answer_context = call_llm(self.llm_model, context_prompt, temperature= 0.1)
            answer_no_context = call_llm(self.llm_model, no_context_prompt, temperature= 0.1)
            #write answer in df
            answers.append({
                'question': question,
                'answer_context': answer_context,
                'answer_no_context': answer_no_context
            })
        answer_df = pd.DataFrame(answers)
        #save df to csv
        answer_df.to_csv('Evaluation/Results/answers.csv', index=False)

if __name__ == "__main__":
    evaluator = Evaluation()
    evaluator.add_pdf_to_db("Literature")
    evaluator.evaluate()
    print("Evaluation completed and results saved to 'Evaluation/Results/answers.csv'.")