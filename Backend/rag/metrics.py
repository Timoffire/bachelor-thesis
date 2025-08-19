
from typing import Dict, Optional
import yfinance as yf
import requests
import pycountry

class CompanyMetricsRetriever:
    def __init__(self, ticker: str):
        self.stock = yf.Ticker(ticker)

    def get_company_info(self) -> Optional[Dict]:
        info = self.stock.info
        company_info = {
            'name': info.get('longName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'employees': info.get('fullTimeEmployees'),
            'market_cap': info.get('marketCap'),
            'description': (info.get('longBusinessSummary') or "Keine Beschreibung verfügbar.")[:500] + '...',
            'headquarters': f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}",
            'website': info.get('website')
        }

        return company_info

    def get_current_metrics(self) -> Optional[Dict]:
        #TODO: Load Metrics via API and return them in a Dictionary
        info = self.stock.info
        # Mapping von unseren standardisierten Namen zu den yfinance-Feldnamen.
        metric_mapping = {
            #EPS
            'eps_direct' : info.get("trailingEps"),
            #P/E Ratio
            'pe_ratio_direct': info.get("trailingPE"),
            #ROA
            'roa_direct': info.get("returnOnAssets"),
            #Price to Book Ratio
            'pb_ratio_direct': info.get("priceToBook"),
            #ROE
            'roe_direct': info.get("returnOnEquity"),
            #Debt to Equity Ratio
            'debt_to_equity_direct': info.get("debtToEquity"),
            #Market Cap
            'market_cap_direct': info.get("marketCap"),
            #Prices to Sales Ratio
            'price_to_sales_direct': info.get("priceToSalesTrailing12Months")
        }
        return {
            "metrics": metric_mapping
        }

    def get_historical_metrics(self):
        stock = self.stock
        income = stock.financials
        balance = stock.balance_sheet
        cashflow = stock.cashflow

        metrics_by_year = {}

        for year in income.columns:
            metrics_by_year[year.year] = {}

            revenue = income.get(year).get("Total Revenue")
            net_income = income.get(year).get("Net Income")
            equity = balance.get(year).get("Total Stockholder Equity")
            total_debt = balance.get(year).get("Total Debt")
            fcf = cashflow.get(year).get("Free Cash Flow")
            #TODO: Add more metrics

            metrics_by_year[year.year] = {
                "revenue": revenue,
                "net_income": net_income,
                "total_debt": total_debt,
                "free_cash_flow": fcf,
                # TODO: Add more metrics
            }
        #TODO: calculate ratios

        return metrics_by_year

    def get_peer_metrics(self):
        info = self.stock.info
        sector = info.get("sector")
        # Dictionary mapping GICS sectors to well-known ETFs
        sector_etf_map = {
            "Technology": "XLK",
            "Health Care": "XLV",
            "Financial Services": "XLF",
            "Consumer Cyclical": "XLY",
            "Consumer Defensive": "XLP",
            "Energy": "XLE",
            "Industrials": "XLI",
            "Materials": "XLB",
            "Utilities": "XLU",
            "Real Estate": "XLRE",
            "Communication Services": "XLC"
        }
        etf_ticker = sector_etf_map.get(sector)
        etf = yf.Ticker(etf_ticker)
        info = etf.info
        insights = {
            "Sector": sector,
            "ETF Symbol": etf_ticker,
            "ETF Name": info.get("longName", "N/A"),
            "YTD Return": info.get("ytdReturn", "N/A"),
            "1Y Return": info.get("threeYearAverageReturn", "N/A"),
            "Total Assets": info.get("totalAssets", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "Beta": info.get("beta", "N/A")
        }
        return insights

    def get_indicator_value(self, country_code, indicator, year):
        url = f'https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=1&date={year}'
        response = requests.get(url)

        if response.status_code != 200:
            return None

        data = response.json()
        if isinstance(data, list) and len(data) > 1 and data[1]:
            return data[1][0].get('value')
        return None

    def get_macro_info(self):
        info = self.stock.info
        yf_country = info.get('country')
        year = 2024
        try:
            country = pycountry.countries.get(name=yf_country).alpha_3
        except:
            return {"error": f"Invalid country name: {yf_country}"}

        indicators = {
            "gdp_growth": "NY.GDP.MKTP.KD.ZG",
            "inflation_rate": "FP.CPI.TOTL.ZG",
            "imports": "NE.IMP.GNFS.ZS",
            "exports": "NE.EXP.GNFS.ZS"
        }

        results = {"country": country}
        for key, code in indicators.items():
            value = self.get_indicator_value(country, code, year)
            results[key] = value

        return results


    def get_metrics(self):
        #orchestrates the functions
        current_metrics = self.get_current_metrics()
        historical_metrics = self.get_historical_metrics()
        peer_metrics = self.get_peer_metrics()
        macro_info = self.get_macro_info()
        company_info = self.get_company_info()

        return {
            "metrics": current_metrics,
            "historical_metrics": historical_metrics,
            "peer_metrics": peer_metrics,
            "macro_info": macro_info,
            "company_info": company_info
        }
