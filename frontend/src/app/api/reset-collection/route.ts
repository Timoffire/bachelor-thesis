/**
 * 🧹 API: Reset Collection (DB zurücksetzen)
 *
 * Zweck:
 *  - Ruft das FastAPI-Backend unter DELETE /api/collection auf
 *  - Setzt damit die Datenbank/Collection zurück (entspricht pipeline.delete_collection())
 *
 * Nutzung:
 *  - POST /api/reset-collection
 *
 * Voraussetzungen:
 *  - FastAPI läuft lokal auf http://localhost:8000 (oder via FASTAPI_BASE_URL in .env.local anpassen)
 *
 * Antwort-Beispiel:
 *  {
 *    "message": "Collection zurückgesetzt",
 *    "backend": { "message": "Collection gelöscht" }
 *  }
 */

import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Optional per .env.local anpassen (ohne trailing slash)
const FASTAPI_BASE_URL =
  process.env.FASTAPI_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

export async function POST() {
  const url = `${FASTAPI_BASE_URL}/api/collection`;

  try {
    const res = await fetch(url, { method: "DELETE" });
    const backend = await res.json().catch(() => ({}));

    if (!res.ok) {
      return NextResponse.json(
        {
          error: "Backend-Reset fehlgeschlagen",
          status: res.status,
          backend,
          fastapi_url: url,
        },
        { status: 502 }
      );
    }

    return NextResponse.json(
      {
        message: "Collection zurückgesetzt",
        backend,
      },
      { status: 200 }
    );
  } catch (e: any) {
    return NextResponse.json(
      {
        error: e?.message ?? "Unbekannter Fehler in reset-collection",
        hint:
          "Läuft FastAPI lokal? Stimmt FASTAPI_BASE_URL? Erreichbar: DELETE /api/collection?",
        fastapi_url: url,
      },
      { status: 500 }
    );
  }
}
