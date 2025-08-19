import json
import logging
from pipeline import RAGPipeline  # Deine Hauptklasse importieren
from metrics import CompanyMetricsRetriever
logging.basicConfig(level=logging.INFO)

def test_run_pipeline():
    ticker = "AAPL"  # Test-Ticker (Apple Inc.)
    pipeline = RAGPipeline(
        persist_directory="./chroma_db",
        collection_name="docs",
        embedding_model="nomic-embed-text",
        llm_model="llama3"
    )

    result = pipeline.run(ticker)
    print(json.dumps(result, indent=4, ensure_ascii=False))

def test_metric_retrieval(ticker):
    retriever = CompanyMetricsRetriever(ticker)
    metrics = retriever.get_current_metrics()
    print("\n===== METRICS ABGERUFEN =====")
    print(json.dumps(metrics, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    #test_metric_retrieval("AAPL")
    test_run_pipeline()