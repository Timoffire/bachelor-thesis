from typing import List, Dict

def build_prompt(ticker: str, metrics: List[str], context: str, metric_values: dict) -> str:
    """
    Erstellt für jede Metrik einen maßgeschneiderten Prompt-Abschnitt und kombiniert diese zu einem Gesamtprompt.
    """
    # Kombiniere System- und User-Message zu einem einzigen Prompt-String
    system_message = (
        "You are a senior financial analyst with expertise in stock metrics analysis. "
        "Provide clear, structured insights for each metric."
    )
    metrics_section = "\n".join(
        f"- {metric}: {metric_values.get(metric, 'N/A')}" for metric in metrics
    )
    user_message = (
        f"Stock Ticker: {ticker}\n"
        f"Metrics:\n{metrics_section}\n\n"
        f"Context:\n{context}\n\n"
        "For each metric, provide:\n"
        "1. Definition\n"
        "2. Current situation analysis\n"
        "3. Interpretation for the stock\n"
        "Format the output as JSON array of objects with keys: metric, value, definition, analysis, interpretation."
    )
    prompt = f"SYSTEM:\n{system_message}\n\nUSER:\n{user_message}"
    return prompt
