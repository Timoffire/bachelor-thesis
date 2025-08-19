import json
from typing import Dict, Any, Optional
import textwrap

def build_metric_analysis_prompt(
    ticker: str,
    metric: str,
    value: Optional[float],
    historical_metrics: Dict[str, Any],
    peer_metrics: Dict[str, Any],
    macro_info: Dict[str, Any],
    company_info: Dict[str, Any],
    literature_context: Optional[str] = None
) -> str:
    payload = {
        "ticker": ticker,
        "metric": metric,
        "value": value,  # may be None
        "historical_metrics": historical_metrics or {},
        "peer_metrics": peer_metrics or {},
        "macro_info": macro_info or {},
        "company_info": company_info or {},
        "literature_context": literature_context or "",
    }

    data_json = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, default=str)

    prompt = f"""
    You are an equity analyst. Your sole task is to interpret a single fundamental metric for one company in plain English for a general audience. Do not predict whether the stock will go up or down. Do not give investment advice. Do not provide forward-looking statements or guidance.

    ### Task
    - Explain what the metric is and what it measures.
    - Interpret the provided current value (if present) in simple terms.
    - Use the historical data to describe trend or stability, if available.
    - Use peer/industry context only to help a layperson understand whether the level is typical or unusual.
    - Briefly mention any macro or company-specific context that meaningfully affects interpretation of this metric.
    - State limitations and what this metric does NOT tell us.
    - Keep the tone neutral, factual, and educational.

    ### Rules (must-follow)
    1) **No predictions** (no “will rise/fall”, no target prices, no timing).
    2) **No advice** (no “buy/sell/hold”, no allocation or suitability statements).
    3) **No fabrication**: Use ONLY the data provided below; if something is missing, say “not provided”.
    4) **Jargon**: Avoid it; if used, define it in one short clause.
    5) **Comparisons**: When comparing, prefer “relative to its own history” and “relative to peers in the same industry”, if that data is provided.
    6) **Numbers**: Quote exact numbers from the input; do not invent benchmarks.

    ### Input Data (JSON)
    {data_json}

    ### Output format (use these exact section headings)
    1) Plain-English summary (2–3 sentences)
    2) What this metric measures
    3) Interpretation of the current value
    4) Historical context (trend, variability)
    5) Peer/industry comparison
    6) Context that may affect interpretation (macro & company specifics)
    7) Limitations & caveats of this metric
    8) One-sentence takeaway (layman-friendly)

    Write the answer in English. Do not include this instruction block in your reply.
    """.strip()

    return textwrap.dedent(prompt)