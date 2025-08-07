from metrics import CompanyMetricsRetriever
import json
from pipeline import RAGPipeline
# Initialize the pipeline
pipeline = RAGPipeline()
info = pipeline.run("AAPL")
#metric = CompanyMetricsRetriever("AAPL")
#info = metric.get_current_metrics()

print(json.dumps(info, indent=4, ensure_ascii=False))