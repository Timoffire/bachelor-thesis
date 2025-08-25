import type { RunRequest, RunResponse, APIError } from '@/types/api';

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, '') ?? '';

function toAPIError(e: unknown, fallback = 'Unbekannter Fehler'): APIError {
  if (e instanceof Response) {
    return { status: e.status, message: `API-Fehler ${e.status}` };
  }
  if (e && typeof e === 'object' && 'message' in e) {
    return { status: 0, message: String((e as any).message) };
  }
  return { status: 0, message: fallback };
}

export async function runTicker(ticker: string): Promise<RunResponse> {
  try {
    const res = await fetch(`${BASE}/api/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // Wichtig: App-Router + Edge/Node kompatibel
      body: JSON.stringify({ ticker } as RunRequest),
      // Optional: CORS, Credentials etc. hier steuern
    });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(text || `HTTP ${res.status}`);
    }
    return (await res.json()) as RunResponse;
  } catch (err) {
    const apiErr = toAPIError(err, 'Konnte /api/run nicht aufrufen');
    throw apiErr;
  }
}
