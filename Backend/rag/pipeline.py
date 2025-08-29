import json
from .vectordb import ChromaDBConnector
from .prompt_engineering import build_metric_analysis_prompt
from .metrics import CompanyMetricsRetriever
from .llm import call_llm, test_model_availability, check_ollama_connection
import os
from dotenv import load_dotenv
from .query_builder import MetricQueryBuilder
import logging
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class RAGPipeline:
    """
    Orchestrates the Retrieval-Augmented Generation (RAG) process by integrating
    document ingestion, querying, and LLM interaction.
    """
    def __init__(self, persist_directory: str = "rag/chroma_db", collection_name: str = "docs", embedding_model: str = "mxbai-embed-large:latest", llm_model: str = "llama3"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.db_connector = ChromaDBConnector(
            path=self.persist_directory,
            embedding_model=self.embedding_model
        )
        self.query_builder = MetricQueryBuilder()

    def ingest_pdf_folder(self, folder_path: str):
        """
        Adds all PDF documents from the specified folder to the ChromaDB collection.
        """
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(folder_path, filename)
                self.db_connector.add_pdf_to_collection(pdf_path)

    def query(self, query_text: str, n_results: int = 10) -> tuple[str, list[str]]:
        """
        Queries the ChromaDB collection for relevant documents based on the input query text.
        Args:
            query_text (str): The input query text.
            n_results (int): The number of top results to retrieve (default: 10).
        Returns:
            A tuple containing:
                - context (str): The concatenated text of the retrieved documents.
                - sources (list[str]): A list of document IDs corresponding to the retrieved documents.
        """
        try:
            #Query the database for relevant documents
            results = self.db_connector.query_collection(
                query_text=query_text,
                n_results=n_results,
            )

            if not results:
                return "", []

            # Build context and sources
            context_parts = []
            sources = []

            for doc_id, doc_text in results:
                # Only add non-empty document texts to the context
                context_parts.append(doc_text)

                # Add sources on different list
                sources.append(doc_id)

            # Join context parts with double newlines for better readability
            context = "\n\n".join(context_parts)

            return context, sources

        except Exception as e:
            print(f"Fehler bei der Abfrage: {str(e)}")
            return "", []

    def run(self, ticker: str):
        """
        Calls the RAG pipeline for a given ticker symbol.
        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            A dictionary containing the enriched metrics with LLM responses and sources.
        """
        #check if the db is initialized
        if not self.db_connector.client.get_collection("docs"):
            logging.error("Die ChromaDB-Collection 'docs' existiert nicht. Bitte fügen Sie Dokumente hinzu oder initialisieren Sie die Collection.")
            return {"error": "Die ChromaDB-Collection 'docs' existiert nicht."}
        #Get all information for the given ticker
        retriever = CompanyMetricsRetriever(ticker)
        complete_metrics = retriever.get_metrics()

        #Splits the complete metrics into its components
        metrics = complete_metrics["metrics"]
        historical_metrics = complete_metrics["historical_metrics"]
        peer_metrics = complete_metrics["peer_metrics"]
        macro_info = complete_metrics["macro_info"]
        company_info = complete_metrics["company_info"]

        #Enriches the metrics with RAG
        enriched_metrics = {}
        for metric, value in metrics["metrics"].items():
            query = self.query_builder.build_query(metric)
            context, sources = self.query(query_text=query)
            enriched_metrics[metric] = {
                "value": value,
                "context": context,
                "sources": sources
            }

        #Builds the LLM prompts and calls the LLM
        responses = {}
        for metric, metric_values in enriched_metrics.items():
            value = metric_values["value"]
            context = metric_values["context"]
            sources = metric_values["sources"]
            prompt = build_metric_analysis_prompt(
                ticker=ticker,
                peer_metrics=peer_metrics,
                macro_info=macro_info,
                company_info=company_info,
                historical_metrics=historical_metrics,
                metric=metric,
                value=value,
                literature_context=context
            )
            llm_response = call_llm(prompt, self.llm_model, temperature=0.01)
            responses[metric] = {
                "value": value,
                "llm_response": llm_response,
                "sources": sources
            }
        return responses

    def delete_collection(self):
        self.db_connector.delete_collection()

    def add_document(self, path: str):
        self.db_connector.add_pdf_to_collection(path)

