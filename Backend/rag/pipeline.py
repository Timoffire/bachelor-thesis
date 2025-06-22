from typing import Union, Any
from vectordb import ChromaDBConnector
from prompt_engineering import build_prompt
from metrics import get_stock_metrics
from llm import call_llm
import os
from dotenv import load_dotenv
from query_builder import MetricQueryBuilder
load_dotenv()

class RAGPipeline:
    #TODO: Komplette Klasse überarbeiten
    """
    Orchestriert die RAG-Pipeline: Retrieval, Augmentation, Prompting.
    """
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "docs", embedding_model: str = "nomic-embed-text", llm_model: str = "llama3"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.db_connector = ChromaDBConnector()
        self.query_builder = MetricQueryBuilder()

    def ingest_pdf_folder(self, folder_path: str):
        """
        Fügt alle PDFs im angegebenen Ordner zur Collection hinzu.
        """
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(folder_path, filename)
                self.db_connector.add_pdf_to_collection(pdf_path)

    def query(self, query_text: str, n_results: int = 5, include_metadata: bool = True) -> tuple[str, list[str]]:
        """
        Führt eine Abfrage gegen die ChromaDB durch und gibt Kontext und Quellen zurück.

        Args:
            query_text: Der Suchtext für die Abfrage
            n_results: Anzahl der zurückzugebenden Ergebnisse (Standard: 5)
            include_metadata: Ob Metadaten in die Quellen einbezogen werden sollen

        Returns:
            tuple: (context, sources)
                - context: Zusammengefügter Text aller gefundenen Dokumente
                - sources: Liste der Quellen-IDs oder Metadaten
        """
        try:
            # Abfrage an ChromaDB
            results = self.db_connector.query_collection(
                query_text=query_text,
                n_results=n_results,
            )

            if not results:
                return "", []

            # Kontext aus allen gefundenen Dokumenten zusammenbauen
            context_parts = []
            sources = []

            for doc_id, doc_text in results:
                # Nur den Dokument-Text zum Kontext hinzufügen (ohne Quellenangabe)
                context_parts.append(doc_text)

                # Quelle zur separaten Liste hinzufügen
                sources.append(doc_id)

            # Gesamten Kontext zusammenfügen
            context = "\n\n".join(context_parts)

            return context, sources

        except Exception as e:
            print(f"Fehler bei der Abfrage: {str(e)}")
            return "", []

    def run(self, ticker: str, metrics: list, embedding_model: str = None, llm_model: str = None) -> dict[
        str, Union[str, list[Any]]]:
        stock_metrics = get_stock_metrics(ticker, metrics)
        responses = []
        all_sources = []

        if embedding_model:
            self.embedding_model = embedding_model
            self.db_connector = ChromaDBConnector(path = self.persist_directory, embedding_model=self.embedding_model)
        if llm_model:
            self.llm_model = llm_model
        for metric in metrics:
            #query text builder
            query_text = self.query_builder.build_query(ticker, metric)
            # Get context and sources
            context, sources = self.query(query_text, n_results=5, include_metadata=True)
            # Build prompt
            prompt = build_prompt(ticker, metrics, context, stock_metrics)
            # Call LLM for each prompt
            response = call_llm(prompt, model_name= self.llm_model)
            #List of responses for each metric
            responses.append(response)
            all_sources.append(sources)
        return {
            'ticker': ticker,
            'responses': responses,
            'all_sources': list(set(all_sources))  # Entferne Duplikate
        }

    def delete_collection(self):
        self.db_connector.delete_collection()

    def add_document(self, path: str):
        self.db_connector.add_pdf_to_collection(path)

    def check_health(self):
        #TODO: Check Health of Backend