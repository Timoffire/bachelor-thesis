/**
 * 💾 API: Last Run (Persistenz für das letzte Run-Ergebnis)
 *
 * Endpoints:
 *  - GET    /api/last-run    → liefert das zuletzt gespeicherte run()-JSON
 *  - DELETE /api/last-run    → löscht den gespeicherten Stand
 *
 * Speichert lokal unter: <projectRoot>/.data/last-run.json
 * Struktur der gespeicherten Datei (Envelope):
 *  {
 *    "savedAt": "ISO-String",
 *    "ticker": "AAPL" | null,
 *    "data":   <das originale JSON der FastAPI /api/run Antwort (responses/results)>
 *  }
 *
 * Hinweis:
 *  - POST ist optional (für manuelles Setzen); das Speichern übernimmt jetzt /api/run.
 */

import { NextResponse } from "next/server";
import path from "path";
import { mkdir, readFile, rm, stat, access } from "fs/promises";
import { constants as fsConstants } from "fs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const DATA_DIR = path.join(process.cwd(), ".data");
const LAST_RUN_FILE = path.join(DATA_DIR, "last-run.json");

async function ensureDir() {
  try {
    await access(DATA_DIR, fsConstants.F_OK);
  } catch {
    await mkdir(DATA_DIR, { recursive: true });
  }
}

export async function GET() {
  try {
    await ensureDir();
    const buf = await readFile(LAST_RUN_FILE);
    const json = JSON.parse(buf.toString("utf-8"));
    const st = await stat(LAST_RUN_FILE);

    // Wir geben direkt das eigentliche run()-JSON unter "data" zurück.
    return NextResponse.json({
      exists: true,
      data: json.data,                 // ← das aktuelle run()-JSON
      meta: { ticker: json.ticker ?? null, savedAt: st.mtime.toISOString() },
      path: LAST_RUN_FILE,
    });
  } catch {
    return NextResponse.json({
      exists: false,
      data: null,
      meta: { ticker: null, savedAt: null },
      path: LAST_RUN_FILE,
    });
  }
}

export async function DELETE() {
  try {
    await ensureDir();
    await rm(LAST_RUN_FILE, { force: true });
    return NextResponse.json({ message: "Last run gelöscht", path: LAST_RUN_FILE });
  } catch (e: any) {
    return NextResponse.json(
      { error: e?.message ?? "Unbekannter Fehler beim Löschen von last-run" },
      { status: 500 }
    );
  }
}
