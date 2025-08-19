import json
from typing import Dict, Any, Optional

def build_metric_analysis_prompt(
    ticker: str,
    metric: str,
    value: Optional[float],
    historical_metrics: Dict[str, Any],
    peer_metrics: Dict[str, Any],
    macro_info: Dict[str, Any],
    company_info: Dict[str, Any],
    literature_context: Optional[str] = None,
    sources: Optional[Dict[str, str]] = None
) -> str:

    return ""