from pipeline import RAGPipeline
import json

if __name__ == "__main__":
    pipeline = RAGPipeline()
    pipeline.add_document("/Users/timmichalow/Desktop/Uni/Bachelorarbeit/Projekt Bachelor/Literatur/Fundamentalanalyse.pdf")
    result = pipeline.run(ticker="AAPL", metrics=["KGV"])

    # Nur die responses ausgeben
    responses = result['responses']

    for i, response in enumerate(responses):
        print(f"Response {i + 1}:")
        try:
            print(json.dumps(response, indent=4, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der JSON-Response: {e}")
            print("Raw Response:", response)
        print("-" * 50)