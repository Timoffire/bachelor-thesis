from pipeline import RAGPipeline
import json

if __name__ == "__main__":
    pipeline = RAGPipeline()
    result = pipeline.run(ticker = "AAPL",metrics= ["revenue", "profit", "net_income"])
    print(json.dumps(result, indent=4, ensure_ascii=False))