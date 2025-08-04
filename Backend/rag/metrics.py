import os
import requests
import logging
import statistics  # Importiert für korrekte Median-Berechnung
from typing import List, Dict, Any
from dotenv import load_dotenv
import yfinance as yf
from datetime import datetime

# Logging-Konfiguration für bessere Übersicht
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CompanyMetricsRetriever:
    def __init__(self):
        #TODO: Load Keys
        #TODO: Innit Logger

    def get_current_metrics(self, ticker: str) -> Dict[str, Any]:
        #TODO: Load Metrics via API and return them in a Dictionary
        #TODO: Load Company Info

    def get_historical_metrics(self, ticker: str):
        #TODO: Load Historic Metrics and return them in a Dictionary

    def get_peer_metrics(self, ticker: str):
        #TODO: find Peer stocks and then get their metrics to compare them later

    def get_macro_metrics(self, ticker: str):
        #TODO: Find the right Country/Market/Sector and load information about them
