class MetricQueryBuilder:

    def __init__(self):
        # Metrik-Keywords in EN und DE
        self.metric_keywords = {
            "eps_direct": ["earnings per share", "EPS", "diluted earnings"],
            "pe_ratio_direct": ["price to earnings", "P/E ratio", "earnings multiple", "valuation"],
            "roa_direct": ["return on assets", "ROA", "asset efficiency", "asset returns"],
            "pb_ratio_direct": ["price to book", "P/B ratio", "book value", "market to book"],
            "roe_direct": ["return on equity", "ROE", "shareholder return", "equity returns"],
            "debt_to_equity_direct": ["debt to equity", "leverage", "financial leverage", "debt ratio"],
            "market_cap_direct": ["market capitalization", "market cap", "market value", "equity value"],
            "price_to_sales_direct": ["price to sales", "P/S ratio", "sales multiple"]
        }

    def build_query(self, metric: str) -> str:
        """
        Creates a query string based on the specified financial metric.
        Args:
            metric: The financial metric to build the query for (e.g., "P/E Ratio
        Returns:
            A query string containing relevant keywords for the specified metric.
        """
        keywords = self.metric_keywords.get(metric, [])

        return " ".join(keywords)
