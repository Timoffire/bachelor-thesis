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


def get_stock_metrics(ticker: str, target_metric: str) -> Dict[str, Any]:
    """
    Erweiterte Funktion zur Abfrage von Aktienmetriken mit:
    1. Aktueller Metrikwert
    2. Historische Daten der Metrik
    3. Vergleichsdaten von Branchenunternehmen
    4. Andere Unternehmensdaten zum Abgleich
    5. Qualitative Daten aus Branche und Nachrichten

    Args:
        ticker: Aktiensymbol (z.B. 'AAPL')
        target_metric: Die spezifische Metrik (z.B. 'P/E Ratio', 'Revenue', 'EPS')

    Returns:
        Dictionary mit allen relevanten Daten
    """
    load_dotenv()
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    if not api_key:
        raise RuntimeError('Bitte setze die Umgebungsvariable ALPHA_VANTAGE_API_KEY.')

    result = {
        'ticker': ticker,
        'target_metric': target_metric,
        'timestamp': datetime.now().isoformat(),
        'current_metric_value': {},
        'historical_data': {},
        'peer_comparison': {},
        'company_context': {},
        'qualitative_data': {},
        'error': None
    }

    try:
        # === ÄNDERUNG: Zentraler API-Aufruf für Unternehmensübersicht ===
        # Dies ist die wichtigste Änderung, um redundante API-Aufrufe zu vermeiden.
        overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
        response = requests.get(overview_url, timeout=10)
        response.raise_for_status()
        overview_data = response.json()

        # Prüfen, ob die API gültige Daten zurückgeliefert hat
        if not overview_data or "Symbol" not in overview_data:
            error_msg = f"Keine gültigen Übersichtsdaten für {ticker} erhalten. API-Antwort: {overview_data}"
            raise ValueError(error_msg)

        logging.info(f"Erfolgreich Übersichtsdaten für {ticker} abgerufen.")

        # Die Helper-Funktionen erhalten jetzt das 'overview_data'-Objekt und müssen es nicht selbst abrufen.

        # 1. Aktuelle Metrikwerte abrufen
        result['current_metric_value'] = _get_current_metric(overview_data, target_metric)

        # 2. Historische Daten der Metrik
        result['historical_data'] = _get_historical_metric_data(ticker, target_metric, api_key)

        # 3. Peer-Group Vergleichsdaten
        result['peer_comparison'] = _get_peer_comparison(ticker, target_metric, overview_data, api_key)

        # 4. Andere Unternehmensdaten zum Abgleich
        result['company_context'] = _get_company_context_data(overview_data)

        # 5. Qualitative Daten
        result['qualitative_data'] = _get_qualitative_data(ticker,
                                                           api_key)  # news_api_key durch api_key ersetzt, da AlphaVantage dies oft kombiniert

    except requests.exceptions.RequestException as e:
        logging.error(f"Netzwerkfehler beim Abrufen der Daten für {ticker}: {e}")
        result['error'] = f"Netzwerkfehler: {e}"
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten für {ticker}: {e}")
        result['error'] = str(e)

    return result


# === ÄNDERUNG: Funktion benötigt keinen eigenen API-Aufruf mehr ===
def _get_current_metric(overview_data: Dict[str, Any], metric: str) -> Dict[str, Any]:
    """Ruft den aktuellen Wert der gewünschten Metrik aus den bereitgestellten Übersichtsdaten ab."""
    metric_mappings = {
        'P/E Ratio': 'PERatio', 'EPS': 'EPS', 'Revenue': 'RevenueTTM',
        'Market Cap': 'MarketCapitalization', 'Book Value': 'BookValue',
        'Dividend Yield': 'DividendYield', 'ROE': 'ReturnOnEquityTTM',
        'ROA': 'ReturnOnAssetsTTM', 'Debt/Equity': 'DebtToEquityRatio',
        'Current Ratio': 'CurrentRatio', 'Quick Ratio': 'QuickRatio'
    }
    alpha_vantage_key = metric_mappings.get(metric, metric)

    return {
        'value': overview_data.get(alpha_vantage_key, 'N/A'),
        'currency': overview_data.get('Currency', 'USD'),
        'last_updated': overview_data.get('LatestQuarter', 'N/A')
    }


# === ÄNDERUNG: Ruft _calculate_trend_analysis jetzt mit der korrekten Metrik auf ===
def _get_historical_metric_data(ticker: str, metric: str, api_key: str) -> Dict[str, Any]:
    """Ruft historische Daten ab und führt eine Trendanalyse für die spezifische Metrik durch."""
    historical_data = {'annual_data': {}, 'quarterly_data': {}, 'trend_analysis': {}}
    try:
        functions = ['INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW']
        for function in functions:
            url = f'https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={api_key}'
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if 'annualReports' in data:
                historical_data['annual_data'][function] = data['annualReports'][:5]
            if 'quarterlyReports' in data:
                historical_data['quarterly_data'][function] = data['quarterlyReports'][:12]

        logging.info(f"Historische Finanzberichte für {ticker} abgerufen.")

        # Trendanalyse wird jetzt für die 'target_metric' durchgeführt
        historical_data['trend_analysis'] = _calculate_trend_analysis(
            historical_data['annual_data'], metric
        )
    except Exception as e:
        logging.error(f"Fehler beim Abrufen historischer Daten für {ticker}: {e}")
        historical_data['error'] = str(e)
    return historical_data


# === ÄNDERUNG: Funktion benötigt keinen eigenen API-Aufruf für den Haupt-Ticker mehr ===
def _get_peer_comparison(ticker: str, metric: str, overview_data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Ruft Vergleichsdaten von Branchenunternehmen ab."""
    peer_data = {'industry_average': None, 'peer_companies': {}, 'industry_info': {}}
    try:
        industry = overview_data.get('Industry', '')
        sector = overview_data.get('Sector', '')
        peer_data['industry_info'] = {'industry': industry, 'sector': sector}

        peer_tickers = _get_peer_tickers(sector, ticker)
        logging.info(f"Vergleiche {ticker} mit Peers: {peer_tickers}")

        peer_values = []
        metric_key = _get_current_metric({}, metric)[
            'value']  # Kleiner Trick, um den API-Key für die Metrik zu bekommen

        for peer_ticker in peer_tickers:
            try:
                peer_overview = requests.get(
                    f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={peer_ticker}&apikey={api_key}',
                    timeout=10).json()
                value_str = peer_overview.get(metric_key, 'N/A')
                if value_str not in ('N/A', 'None', None):
                    numeric_value = float(value_str)
                    peer_data['peer_companies'][peer_ticker] = {'value': numeric_value}
                    peer_values.append(numeric_value)
            except (requests.exceptions.RequestException, ValueError, TypeError) as e:
                logging.warning(f"Fehler beim Abrufen von Peer-Daten für {peer_ticker}: {e}")

        # === ÄNDERUNG: Korrekte statistische Berechnungen ===
        if peer_values:
            peer_data['industry_average'] = {
                'mean': round(statistics.mean(peer_values), 2),
                'median': round(statistics.median(peer_values), 2),
                'min': min(peer_values),
                'max': max(peer_values),
                'sample_size': len(peer_values)
            }
    except Exception as e:
        logging.error(f"Fehler beim Peer-Vergleich für {ticker}: {e}")
        peer_data['error'] = str(e)
    return peer_data


# === ÄNDERUNG: Funktion benötigt keinen eigenen API-Aufruf mehr ===
def _get_company_context_data(overview_data: Dict[str, Any]) -> Dict[str, Any]:
    """Stellt zusätzliche Unternehmensdaten aus den bereitgestellten Übersichtsdaten zusammen."""
    data = overview_data
    return {
        'financial_health': {
            'debt_to_equity': data.get('DebtToEquityRatio', 'N/A'),
            'current_ratio': data.get('CurrentRatio', 'N/A'),
        },
        'growth_metrics': {
            'revenue_growth_ttm': data.get('QuarterlyRevenueGrowthYOY', 'N/A'),
            'earnings_growth': data.get('QuarterlyEarningsGrowthYOY', 'N/A'),
        },
        'profitability': {
            'roe': data.get('ReturnOnEquityTTM', 'N/A'),
            'roa': data.get('ReturnOnAssetsTTM', 'N/A'),
            'profit_margin': data.get('ProfitMargin', 'N/A'),
        },
        'valuation': {
            'pe_ratio': data.get('PERatio', 'N/A'),
            'peg_ratio': data.get('PEGRatio', 'N/A'),
            'price_to_book': data.get('PriceToBookRatio', 'N/A'),
        },
        'dividend_info': {
            'dividend_yield': data.get('DividendYield', 'N/A'),
            'dividend_per_share': data.get('DividendPerShare', 'N/A'),
        }
    }


# Unverändert, aber weiterhin eine Vereinfachung. Für einen Prototyp ok.
def _get_peer_tickers(sector: str, exclude_ticker: str) -> List[str]:
    """Gibt eine hartcodierte Liste von Peer-Unternehmen basierend auf dem Sektor zurück."""
    sector_peers = {
        'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA'],
        'Healthcare': ['JNJ', 'PFE', 'ABBV', 'MRK', 'TMO'],
        'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
        # ... weitere Sektoren hier hinzufügen
    }
    peers = sector_peers.get(sector, [])
    return [t for t in peers if t != exclude_ticker][:4]  # Max 4 Peers, um API-Limits zu schonen


# === ÄNDERUNG: Diese Funktion ist jetzt dynamisch und analysiert die Zielmetrik ===
def _calculate_trend_analysis(annual_data: Dict[str, Any], metric: str) -> Dict[str, Any]:
    """Berechnet eine Trendanalyse für die angegebene Metrik aus den historischen Daten."""
    trend_analysis = {'trend_found': False}

    # Mapping von benutzerfreundlichen Metriken zu den Feldern in den Alpha Vantage Berichten
    metric_to_financial_report_mapping = {
        'Revenue': ('INCOME_STATEMENT', 'totalRevenue'),
        'Net Income': ('INCOME_STATEMENT', 'netIncome'),
        'EPS': ('INCOME_STATEMENT', 'reportedEPS'),  # 'reportedEPS' statt 'earningsPerShare' für Konsistenz
        'Total Assets': ('BALANCE_SHEET', 'totalAssets'),
        'Total Debt': ('BALANCE_SHEET', 'totalLiabilities'),  # Oft wird 'totalLiabilities' als Annäherung genommen
    }

    if metric not in metric_to_financial_report_mapping:
        trend_analysis['message'] = f"Trendanalyse für '{metric}' wird nicht unterstützt."
        return trend_analysis

    report_name, field_name = metric_to_financial_report_mapping[metric]

    if report_name not in annual_data or not annual_data[report_name]:
        trend_analysis['message'] = f"Keine Jahresberichte für '{report_name}' gefunden."
        return trend_analysis

    values = []
    for report in annual_data[report_name]:
        value_str = report.get(field_name, '0')
        try:
            values.append(float(value_str))
        except (ValueError, TypeError):
            continue

    # Werte sind oft chronologisch von neu nach alt, für CAGR umdrehen
    values.reverse()

    if len(values) >= 2:
        trend_analysis['trend_found'] = True
        trend_analysis['years_analyzed'] = len(values)
        trend_analysis['values'] = values

        # CAGR (Compound Annual Growth Rate) berechnen
        try:
            cagr = ((values[-1] / values[0]) ** (1 / (len(values) - 1)) - 1) * 100
            trend_analysis['cagr_percent'] = round(cagr, 2)
            if cagr > 5:
                trend_analysis['trend_direction'] = 'growing'
            elif cagr < -5:
                trend_analysis['trend_direction'] = 'declining'
            else:
                trend_analysis['trend_direction'] = 'stable'
        except (ZeroDivisionError, ValueError):
            trend_analysis['cagr_percent'] = 'N/A'  # z.B. bei Division durch Null
            trend_analysis['trend_direction'] = 'unclear'

    return trend_analysis


def _get_qualitative_data(ticker: str, api_key: str) -> Dict[str, Any]:
    """Ruft qualitative Daten wie Nachrichten und Analystenempfehlungen ab."""
    # Diese Funktion bleibt weitgehend gleich, verwendet yfinance als gute Ergänzung.
    qualitative_data = {'recent_news': [], 'analyst_recommendations': {}}
    try:
        # Alpha Vantage News (falls im API-Plan enthalten)
        news_url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={api_key}'
        news_response = requests.get(news_url, timeout=15)
        if news_response.status_code == 200:
            news_data = news_response.json()
            if 'feed' in news_data:
                qualitative_data['recent_news'] = news_data['feed'][:5]  # Letzte 5 Artikel
                logging.info(f"Nachrichten für {ticker} von Alpha Vantage abgerufen.")

        # Yahoo Finance für Analystenempfehlungen
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            qualitative_data['analyst_recommendations'] = {
                'latest': recommendations.tail(5).to_dict('records'),
                'summary': stock.info.get('recommendationKey', 'N/A')
            }
            logging.info(f"Analystendaten für {ticker} von Yahoo Finance abgerufen.")

    except Exception as e:
        logging.warning(f"Fehler beim Abrufen qualitativer Daten für {ticker}: {e}")
        qualitative_data['error'] = str(e)

    return qualitative_data