/**
 * 🚀 API: Run (Ticker-Analyse)
 *
 * Zweck:
 *  - Ruft FastAPI /api/run mit { ticker } auf
 *  - Speichert bei Erfolg die FastAPI-Antwort unter .data/last-run.json (überschreibt)
 *  - Gibt dem Client das Ergebnis zurück
 *
 * Request:
 *  POST /api/run
 *  { "ticker": "AAPL" }
 *
 * Response (Beispiel):
 *  {
 *    "message": "Run erfolgreich",
 *    "ticker": "AAPL",
 *    "saved": true,
 *    "savedAt": "2025-08-27T12:34:56.000Z",
 *    "backend": <originale FastAPI-JSON-Antwort>
 *  }
 */

import { NextResponse } from "next/server";
import path from "path";
import { mkdir, writeFile, access } from "fs/promises";
import { constants as fsConstants } from "fs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const FASTAPI_BASE_URL =
  process.env.FASTAPI_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

// Persistenz-Ziele (wie /api/last-run)
const DATA_DIR = path.join(process.cwd(), ".data");
const LAST_RUN_FILE = path.join(DATA_DIR, "last-run.json");

async function ensureDir() {
  try {
    await access(DATA_DIR, fsConstants.F_OK);
  } catch {
    await mkdir(DATA_DIR, { recursive: true });
  }
}

/** Speichert das Ergebnis als last-run (überschreibt immer) */
async function saveLastRun(ticker: string | null, backendJson: any) {
  await ensureDir();
  const envelope = {
    savedAt: new Date().toISOString(),
    ticker,
    data: backendJson, // ← exakt das FastAPI-run()-JSON (responses/results)
  };
  await writeFile(LAST_RUN_FILE, JSON.stringify(envelope, null, 2), "utf-8");
  return envelope.savedAt;
}

export async function POST(req: Request) {
  const url = `${FASTAPI_BASE_URL}/api/run`;

  try {
    const body = await req.json().catch(() => null);
    if (!body?.ticker || typeof body.ticker !== "string") {
      return NextResponse.json(
        { error: "Ticker fehlt oder ist ungültig. Sende { ticker: 'AAPL' }" },
        { status: 400 }
      );
    }

    // 1) FastAPI aufrufen
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: body.ticker }),
    });

    const backend = await res.json().catch(() => ({}));

    if (!res.ok) {
      return NextResponse.json(
        {
          error: "Backend-Run fehlgeschlagen",
          status: res.status,
          backend,
          fastapi_url: url,
          sent: { ticker: body.ticker },
        },
        { status: 502 }
      );
    }

    // 2) Bei Erfolg: last-run überschreiben
    const savedAt = await saveLastRun(body.ticker, backend);

    // 3) Client-Antwort
    return NextResponse.json(
      {
        message: "Run erfolgreich",
        ticker: body.ticker,
        saved: true,
        savedAt,
        backend, // komplette FastAPI-Antwort (8 Metriken JSON)
      },
      { status: 200 }
    );
  } catch (e: any) {
    return NextResponse.json(
      {
        error: e?.message ?? "Unbekannter Fehler in run-API",
        hint:
          "Läuft FastAPI lokal? Stimmt FASTAPI_BASE_URL? Erwartet POST /api/run mit {ticker}.",
        fastapi_url: url,
      },
      { status: 500 }
    );
  }
}
