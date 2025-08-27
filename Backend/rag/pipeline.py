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
    Orchestriert die RAG-Pipeline: Retrieval, Augmentation, Prompting.
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
        Fügt alle PDFs im angegebenen Ordner zur Collection hinzu.
        """
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(folder_path, filename)
                self.db_connector.add_pdf_to_collection(pdf_path)

    def query(self, query_text: str, n_results: int = 10) -> tuple[str, list[str]]:
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

    def run(self, ticker: str):
        """
        Calls the RAG pipeline for a given ticker symbol.
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
            llm_response = call_llm(prompt, self.llm_model, temperature=0.5)
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

    def check_health(self) -> str:
        """
                Führt einen Health Check für die Pipeline-Komponenten durch und gibt
                den Status als JSON-String zurück.

                Returns:
                    str: Ein JSON-String, der den Status der Komponenten beschreibt.
                """
        health_status = {
            "database": {"status": "UNKNOWN", "details": ""},
            "llm": {"status": "UNKNOWN", "details": ""}
        }

        # 1. Prüfe ChromaDB Server und Collection
        try:
            # Schritt 1: Prüfen, ob der DB-Server erreichbar ist (Standardmethode)
            self.db_connector.client.heartbeat()

            # Schritt 2: Prüfen, ob die spezifische Collection existiert
            # Der Versuch, die Collection abzurufen, ist der zuverlässigste Check.
            self.db_connector.client.get_collection(name=self.collection_name)

            health_status["database"]["status"] = "OK"
            health_status["database"][
                "details"] = f"ChromaDB-Server erreichbar und Collection '{self.collection_name}' ist vorhanden."

        except Exception as e:
            # Fängt Fehler von heartbeat() oder get_collection() ab
            health_status["database"]["status"] = "FEHLER"
            health_status["database"][
                "details"] = f"Fehler bei der Verbindung zur ChromaDB oder Collection nicht gefunden: {e}"

        # 2. Prüfe LLM (Ollama) Verbindung und Modellverfügbarkeit
        try:
            if not check_ollama_connection():
                health_status["llm"]["status"] = "FEHLER"
                health_status["llm"]["details"] = "Ollama-Server ist nicht erreichbar."
            else:
                if test_model_availability(self.llm_model):
                    health_status["llm"]["status"] = "OK"
                    health_status["llm"][
                        "details"] = f"Ollama-Server läuft und Modell '{self.llm_model}' ist verfügbar."
                else:
                    health_status["llm"]["status"] = "WARNUNG"
                    health_status["llm"][
                        "details"] = f"Ollama-Server läuft, aber das Modell '{self.llm_model}' ist NICHT verfügbar."
        except Exception as e:
            health_status["llm"]["status"] = "FEHLER"
            health_status["llm"]["details"] = f"Ein unerwarteter Fehler beim Prüfen des LLM ist aufgetreten: {e}"

        # Gebe das Ergebnis als schön formatierten JSON-String zurück
        return json.dumps(health_status, indent=4, ensure_ascii=False)

