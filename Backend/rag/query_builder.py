class MetricQueryBuilder:
    """
    Erstellt optimierte Suchanfragen für verschiedene Finanzmetriken.
    """

    def __init__(self):
        # Basis-Keywords für verschiedene Metrik-Kategorien
        self.metric_keywords = {
            # Umsatz und Wachstum
            "revenue": ["revenue", "sales", "income", "turnover", "net sales", "total revenue"],
            "revenue_growth": ["revenue growth", "sales growth", "year over year revenue", "quarterly revenue"],
            "quarterly_revenue": ["quarterly revenue", "quarterly sales", "Q1 Q2 Q3 Q4 revenue"],

            # Profitabilität
            "net_income": ["net income", "profit", "earnings", "net profit", "bottom line"],
            "gross_profit": ["gross profit", "gross margin", "gross income"],
            "operating_income": ["operating income", "operating profit", "EBIT", "operating earnings"],
            "profit_margin": ["profit margin", "net margin", "profitability", "margin analysis"],
            "gross_margin": ["gross margin", "gross profit margin", "cost of goods sold"],
            "operating_margin": ["operating margin", "operating profit margin", "EBITDA margin"],

            # Rentabilität
            "roe": ["return on equity", "ROE", "shareholder return", "equity returns"],
            "roa": ["return on assets", "ROA", "asset efficiency", "asset returns"],
            "roic": ["return on invested capital", "ROIC", "capital efficiency"],

            # Liquidität
            "current_ratio": ["current ratio", "liquidity", "short term liquidity", "working capital"],
            "quick_ratio": ["quick ratio", "acid test", "immediate liquidity"],
            "cash_ratio": ["cash ratio", "cash position", "cash equivalents"],

            # Verschuldung
            "debt_to_equity": ["debt to equity", "leverage", "financial leverage", "debt ratio"],
            "debt_to_assets": ["debt to assets", "asset coverage", "total debt"],
            "interest_coverage": ["interest coverage", "times interest earned", "debt service"],

            # Bewertung
            "pe_ratio": ["price to earnings", "P/E ratio", "earnings multiple", "valuation"],
            "pb_ratio": ["price to book", "P/B ratio", "book value", "market to book"],
            "ps_ratio": ["price to sales", "P/S ratio", "sales multiple"],
            "ev_ebitda": ["enterprise value", "EV/EBITDA", "enterprise multiple"],

            # Effizienz
            "asset_turnover": ["asset turnover", "asset efficiency", "asset utilization"],
            "inventory_turnover": ["inventory turnover", "inventory management", "stock turnover"],
            "receivables_turnover": ["receivables turnover", "accounts receivable", "collection efficiency"],

            # Dividenden
            "dividend_yield": ["dividend yield", "dividend", "shareholder payout", "dividend policy"],
            "dividend_payout": ["dividend payout ratio", "dividend coverage", "earnings payout"],

            # Cashflow
            "operating_cash_flow": ["operating cash flow", "cash from operations", "OCF"],
            "free_cash_flow": ["free cash flow", "FCF", "cash generation", "capital expenditure"],
            "cash_conversion": ["cash conversion cycle", "working capital cycle"],

            # Marktmetriken
            "market_cap": ["market capitalization", "market cap", "market value", "equity value"],
            "book_value": ["book value", "shareholders equity", "net worth"],
            "earnings_per_share": ["earnings per share", "EPS", "diluted earnings"],

            # Wachstumsmetriken
            "earnings_growth": ["earnings growth", "profit growth", "income growth"],
            "book_value_growth": ["book value growth", "equity growth", "retained earnings"],
            "dividend_growth": ["dividend growth", "dividend increases", "dividend history"]
        }

        # Zusätzliche Kontext-Keywords für bessere Suchergebnisse
        self.context_keywords = [
            "financial performance", "annual report", "quarterly report", "10-K", "10-Q",
            "financial statements", "balance sheet", "income statement", "cash flow statement",
            "management discussion", "MD&A", "financial analysis", "business overview"
        ]

    def build_query(self, ticker: str, metric: str, include_context: bool = True) -> str:
        """
        Erstellt eine optimierte Suchanfrage für eine spezifische Metrik und ein Unternehmen.

        Args:
            ticker: Börsenticker des Unternehmens (z.B. "AAPL")
            metric: Name der Metrik (z.B. "revenue", "profit_margin")
            include_context: Ob zusätzliche Kontext-Keywords hinzugefügt werden sollen

        Returns:
            str: Optimierte Suchanfrage
        """
        # Normalisiere Metrik-Name
        metric_lower = metric.lower().strip()

        # Hole Keywords für die Metrik
        metric_keywords = self.metric_keywords.get(metric_lower, [metric_lower])

        # Baue Basis-Query
        query_parts = [ticker]
        query_parts.extend(metric_keywords[:3])  # Verwende maximal 3 Keywords pro Metrik

        # Füge Kontext-Keywords hinzu wenn gewünscht
        if include_context:
            query_parts.extend(["financial", "analysis"])

        return " ".join(query_parts)