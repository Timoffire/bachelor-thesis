from .vectordb import ChromaDBConnector
from .prompt_engineering import build_prompt
from .metrics import get_stock_metrics
from .llm import call_llm
import os
from dotenv import load_dotenv
load_dotenv()

class RAGPipeline:
    """
    Orchestriert die RAG-Pipeline: Retrieval, Augmentation, Prompting.
    """
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "docs", embedding_model: str = "nomic-embed-text", llm_model: str = "llama3"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.db_connector = ChromaDBConnector(persist_directory=persist_directory)

    def ingest_pdf_folder(self, folder_path: str):
        """
        Fügt alle PDFs im angegebenen Ordner zur Collection hinzu.
        """
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(folder_path, filename)
                self.db_connector.add_pdf_to_collection(pdf_path, collection_name=self.collection_name)

    def query(self, query: str, metric: str, n_results: int = 3):
        """
        Führt eine Retrieval-Abfrage über die ChromaDBConnector-Query-Methode durch.
        Gibt (context, sources) direkt zurück.
        """
        return self.db_connector.query(query, metric, collection_name=self.collection_name, top_k=n_results)

    def run(self, ticker: str, metrics: list, embedding_model: str = None, llm_model: str = None) -> dict:
        stock_metrics = get_stock_metrics(ticker, metrics)
        responses = []
        all_sources = []
        if embedding_model:
            self.embedding_model = embedding_model
            self.db_connector = ChromaDBConnector(persist_directory=self.persist_directory)
        if llm_model:
            self.llm_model = llm_model
        for metric in metrics:
            # Get context and sources
            context, sources = self.query(f"{ticker} {metric}", metric)
            # Build prompt
            prompt = build_prompt(ticker, metrics, context, stock_metrics)
            # Call LLM for each prompt
            response = call_llm(prompt, model_name= self.llm_model)
            #List of responses for each metric
            responses.append(response)
            all_sources.append(sources)
        return responses, all_sources

    def add_document(self, pdf_path: str, collection_name: str = "docs"):
        self.db_connector.add_pdf_to_collection(pdf_path, collection_name=collection_name)
        return {"status": "ok"}