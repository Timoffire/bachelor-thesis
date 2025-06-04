import os
import requests
from typing import List
from dotenv import load_dotenv

# Mapping von Frontend-Metriknamen zu Alphavantage-API-Namen
# Ergänze nach Bedarf weitere Metriken!
METRIC_NAME_MAP_GENERAL = {
    "Marktkapitalisierung": "MarketCapitalization",
    "Umsatz": "RevenueTTM",
    "Gewinn": "GrossProfitTTM",
    "EBITDA": "EBITDA",
    "KGV": "PERatio",
    "Eigenkapitalrendite": "ReturnOnEquityTTM",
}

def get_stock_metrics(ticker: str, metrics: List[str]) -> dict:
    """
    Ruft ausschließlich Werte aus den Financial Statements (Income Statement, Balance Sheet, Cash Flow Statement)
    für den angegebenen Ticker ab und gibt nur die im metrics-Parameter gewünschten Felder zurück.
    Der Alpha Vantage API-Key muss in der Umgebungsvariable ALPHA_VANTAGE_API_KEY liegen.
    """
    load_dotenv()
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        raise RuntimeError('Bitte setze die Umgebungsvariable ALPHA_VANTAGE_API_KEY mit deinem Alpha Vantage API Key.')

    
    # General Company information
    url_company = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    r_company = requests.get(url_company)
    
    # Metriknamen vom Frontend in Alphavantage-Namen umwandeln
    mapped_metrics = [METRIC_NAME_MAP_GENERAL.get(m, m) for m in metrics]

    # Filtere die gewünschten Metriken aus der API-Antwort
    filtered_metrics = {k: v for k, v in r_company.json().items() if k in mapped_metrics}

    return filtered_metrics

