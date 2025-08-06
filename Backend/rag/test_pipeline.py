from metrics import CompanyMetricsRetriever

if __name__ == "__main__":
    print("Starte Skript...")
    metric = CompanyMetricsRetriever("AAPL")
    response = metric.get_macro_info()
    print(response)