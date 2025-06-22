class MetricQueryBuilder:
    """
    Erstellt optimierte Suchanfragen für verschiedene Finanzmetriken.
    Unterstützt sowohl englische als auch deutsche Keywords.
    """

    def __init__(self):
        # Metrik-Keywords in EN und DE
        self.metric_keywords = {
            "revenue": {
                "en": ["revenue", "sales", "income", "turnover", "net sales", "total revenue"],
                "de": ["Umsatz", "Verkäufe", "Erlöse", "Einnahmen", "Gesamterlös"]
            },
            "revenue_growth": {
                "en": ["revenue growth", "sales growth", "year over year revenue", "quarterly revenue"],
                "de": ["Umsatzwachstum", "Verkaufswachstum", "jährliches Umsatzwachstum", "quartalsweiser Umsatz"]
            },
            "quarterly_revenue": {
                "en": ["quarterly revenue", "quarterly sales", "Q1 Q2 Q3 Q4 revenue"],
                "de": ["Quartalsumsatz", "Umsatz Q1 Q2 Q3 Q4"]
            },
            "net_income": {
                "en": ["net income", "profit", "earnings", "net profit", "bottom line"],
                "de": ["Nettogewinn", "Reingewinn", "Ertrag", "Jahresüberschuss"]
            },
            "gross_profit": {
                "en": ["gross profit", "gross margin", "gross income"],
                "de": ["Bruttogewinn", "Rohertrag", "Bruttomarge"]
            },
            "operating_income": {
                "en": ["operating income", "operating profit", "EBIT", "operating earnings"],
                "de": ["Betriebsergebnis", "operativer Gewinn", "EBIT"]
            },
            "profit_margin": {
                "en": ["profit margin", "net margin", "profitability", "margin analysis"],
                "de": ["Gewinnmarge", "Nettomarge", "Rentabilität"]
            },
            "gross_margin": {
                "en": ["gross margin", "gross profit margin", "cost of goods sold"],
                "de": ["Bruttomarge", "Rohertragsmarge", "Wareneinsatz"]
            },
            "operating_margin": {
                "en": ["operating margin", "operating profit margin", "EBITDA margin"],
                "de": ["operative Marge", "EBITDA-Marge", "Betriebsmarge"]
            },
            "roe": {
                "en": ["return on equity", "ROE", "shareholder return", "equity returns"],
                "de": ["Eigenkapitalrendite", "ROE", "Rendite auf Eigenkapital"]
            },
            "roa": {
                "en": ["return on assets", "ROA", "asset efficiency", "asset returns"],
                "de": ["Gesamtkapitalrendite", "ROA", "Kapitalnutzung"]
            },
            "roic": {
                "en": ["return on invested capital", "ROIC", "capital efficiency"],
                "de": ["ROIC", "Kapitalrendite", "Rendite auf investiertes Kapital"]
            },
            "current_ratio": {
                "en": ["current ratio", "liquidity", "short term liquidity", "working capital"],
                "de": ["Liquiditätsgrad", "kurzfristige Liquidität", "Working Capital"]
            },
            "quick_ratio": {
                "en": ["quick ratio", "acid test", "immediate liquidity"],
                "de": ["Schnelltest", "Quick Ratio", "sofortige Liquidität"]
            },
            "cash_ratio": {
                "en": ["cash ratio", "cash position", "cash equivalents"],
                "de": ["Bargeldquote", "Kassenbestand", "liquide Mittel"]
            },
            "debt_to_equity": {
                "en": ["debt to equity", "leverage", "financial leverage", "debt ratio"],
                "de": ["Verschuldungsgrad", "Fremdkapitalquote", "Schulden zu Eigenkapital"]
            },
            "debt_to_assets": {
                "en": ["debt to assets", "asset coverage", "total debt"],
                "de": ["Schulden zu Vermögen", "Vermögensdeckung", "Gesamtschulden"]
            },
            "interest_coverage": {
                "en": ["interest coverage", "times interest earned", "debt service"],
                "de": ["Zinsdeckungsgrad", "Zinsbelastung", "Zinsendienst"]
            },
            "pe_ratio": {
                "en": ["price to earnings", "P/E ratio", "earnings multiple", "valuation"],
                "de": ["Kurs-Gewinn-Verhältnis", "KGV", "Gewinnbewertung", "Unternehmensbewertung"]
            },
            "pb_ratio": {
                "en": ["price to book", "P/B ratio", "book value", "market to book"],
                "de": ["Kurs-Buchwert-Verhältnis", "KBV", "Buchwert"]
            },
            "ps_ratio": {
                "en": ["price to sales", "P/S ratio", "sales multiple"],
                "de": ["Kurs-Umsatz-Verhältnis", "KUV", "Umsatzbewertung"]
            },
            "ev_ebitda": {
                "en": ["enterprise value", "EV/EBITDA", "enterprise multiple"],
                "de": ["Unternehmenswert", "EV/EBITDA", "Multiplikator"]
            },
            "asset_turnover": {
                "en": ["asset turnover", "asset efficiency", "asset utilization"],
                "de": ["Kapitalumschlag", "Anlageneffizienz", "Nutzung des Vermögens"]
            },
            "inventory_turnover": {
                "en": ["inventory turnover", "inventory management", "stock turnover"],
                "de": ["Lagerumschlag", "Lagerhaltung", "Warenumschlag"]
            },
            "receivables_turnover": {
                "en": ["receivables turnover", "accounts receivable", "collection efficiency"],
                "de": ["Forderungsumschlag", "Debitorenumschlag", "Einzugsquote"]
            },
            "dividend_yield": {
                "en": ["dividend yield", "dividend", "shareholder payout", "dividend policy"],
                "de": ["Dividendenrendite", "Dividende", "Ausschüttung", "Dividendenpolitik"]
            },
            "dividend_payout": {
                "en": ["dividend payout ratio", "dividend coverage", "earnings payout"],
                "de": ["Ausschüttungsquote", "Dividendendeckung", "Ertragsausschüttung"]
            },
            "operating_cash_flow": {
                "en": ["operating cash flow", "cash from operations", "OCF"],
                "de": ["operativer Cashflow", "Geldfluss aus Geschäftstätigkeit", "OCF"]
            },
            "free_cash_flow": {
                "en": ["free cash flow", "FCF", "cash generation", "capital expenditure"],
                "de": ["freier Cashflow", "FCF", "Kapitalfluss", "Investitionsausgaben"]
            },
            "cash_conversion": {
                "en": ["cash conversion cycle", "working capital cycle"],
                "de": ["Cash Conversion Cycle", "Working Capital Zyklus"]
            },
            "market_cap": {
                "en": ["market capitalization", "market cap", "market value", "equity value"],
                "de": ["Marktkapitalisierung", "Börsenwert", "Marktwert", "Eigenkapitalwert"]
            },
            "book_value": {
                "en": ["book value", "shareholders equity", "net worth"],
                "de": ["Buchwert", "Eigenkapital", "Nettovermögen"]
            },
            "earnings_per_share": {
                "en": ["earnings per share", "EPS", "diluted earnings"],
                "de": ["Gewinn je Aktie", "EPS", "verwässerter Gewinn"]
            },
            "earnings_growth": {
                "en": ["earnings growth", "profit growth", "income growth"],
                "de": ["Gewinnwachstum", "Ertragswachstum", "Einkommenszuwachs"]
            },
            "book_value_growth": {
                "en": ["book value growth", "equity growth", "retained earnings"],
                "de": ["Buchwertwachstum", "Eigenkapitalwachstum", "Gewinnrücklagen"]
            },
            "dividend_growth": {
                "en": ["dividend growth", "dividend increases", "dividend history"],
                "de": ["Dividendenwachstum", "Dividendensteigerung", "Dividendenhistorie"]
            }
        }

        # Kontext-Keywords für bessere Ergebnisse
        self.context_keywords = {
            "en": ["financial performance", "annual report", "quarterly report", "10-K", "10-Q",
                   "financial statements", "balance sheet", "income statement", "cash flow statement",
                   "management discussion", "MD&A", "financial analysis", "business overview"],
            "de": ["Finanzleistung", "Jahresbericht", "Quartalsbericht", "Finanzkennzahlen",
                   "Bilanz", "GuV", "Kapitalflussrechnung", "Managementbericht", "Analyse", "Unternehmensüberblick"]
        }

    def build_query(self, ticker: str, metric: str, lang: str = "en", include_context: bool = True) -> str:
        """
        Erstellt eine optimierte Suchanfrage für eine spezifische Metrik und ein Unternehmen.
        Args:
            ticker: Börsenticker des Unternehmens (z. B. "AAPL")
            metric: Name der Metrik (z. B. "revenue", "profit_margin")
            lang: Sprache der Suchbegriffe ("en" oder "de")
            include_context: Ob zusätzliche Kontextbegriffe ergänzt werden sollen
        Returns:
            str: Optimierte Suchanfrage
        """
        metric_lower = metric.lower().strip()
        keywords = self.metric_keywords.get(metric_lower, {}).get(lang, [metric_lower])
        query_parts = [ticker.upper()] + keywords[:3]

        if include_context:
            query_parts.extend(self.context_keywords.get(lang, []))

        return " ".join(query_parts)
