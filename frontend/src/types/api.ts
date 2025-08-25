export interface RunRequest {
  ticker: string; // z. B. "AAPL"
}

export interface RunMetricItem {
  value: unknown;
  llm_response: string;
  sources: string[];
}

export interface RunResponse {
  results: Record<string, RunMetricItem>;
}

export interface APIError {
  status: number;
  message: string;
}
