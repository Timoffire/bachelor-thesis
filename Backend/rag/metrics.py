
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import yfinance as yf
import wbdata

class CompanyMetricsRetriever:
    def __init__(self, ticker: str):
        self.stock = yf.Ticker(ticker)

    def get_current_metrics(self) -> Optional[Dict]:
        #TODO: Load Metrics via API and return them in a Dictionary
        info = self.stock.info
        # Mapping von unseren standardisierten Namen zu den yfinance-Feldnamen.
        metric_mapping = {
            'revenue': info.get('totalRevenue'),
            'net_income': info.get('netIncomeToCommon'),
            'total_debt': info.get('totalDebt'),
            'free_cash_flow': info.get('freeCashflow'),
            'roe': info.get('returnOnEquity'),
            'roa': info.get('returnOnAssets'),
            'debt_to_equity': info.get('debtToEquity'),
            'current_ratio': info.get('currentRatio'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'price_to_sales': info.get('priceToSalesTrailing12Months')
            # TODO: choose only 6 relevant stock informations
        }
        # TODO: Load Company Info
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
        return {
            "metrics": metric_mapping,
            "company_info": company_info
        }

    def get_historical_metrics(self):
        #TODO: Load Historic Metrics and return them in a Dictionary
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

        return metrics_by_year

    def get_peer_metrics(self):
        #TODO: find Peer stocks and then get their metrics to compare them later
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

    def get_macro_info(self):
        info = self.stock.info
        country = info.get("country")
        return country


    #def get_metrics(self, ticker: str):
        #orchestrates the functions
        #formats answer --> differ between specific metric and general context (which gets added to every metric)
        #remove all N/A values from the metrics dictionary
        #returns it for later process



