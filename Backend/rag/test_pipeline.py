from pipeline import RAGPipeline
import json

if __name__ == "__main__":
    pipeline = RAGPipeline()
    result = pipeline.run(ticker="AAPL", metrics=["Marktkapitalisierung"])