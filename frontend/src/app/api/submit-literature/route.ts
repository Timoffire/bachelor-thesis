// src/app/api/submit-literature/route.ts
import { NextResponse } from "next/server";
import path from "path";
import { readdir, rm } from "fs/promises";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// ⇨ Optional via .env.local setzen (Fallback: lokales FastAPI)
const FASTAPI_BASE_URL =
  process.env.FASTAPI_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

// Standard-Ordner: <projectRoot>/public/Literature
const LITERATURE_DIR = path.join(process.cwd(), "public", "Literature");

/**
 * Löscht ALLE Inhalte im Ordner, lässt den Ordner selbst aber bestehen.
 */
async function clearDirectoryContents(dir: string) {
  let deleted: string[] = [];
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const abs = path.join(dir, entry.name);
      // rm kann rekursiv Dateien/Ordner entfernen
      await rm(abs, { recursive: true, force: true });
      deleted.push(abs);
    }
  } catch (e) {
    // Wenn der Ordner leer/nicht vorhanden ist, ignorieren wir das still
  }
  return deleted;
}

export async function POST(req: Request) {
  // Erlaube optionales Override via JSON { folder_path: "..." }
  let folderPath = LITERATURE_DIR;
  try {
    const contentType = req.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const body = await req.json().catch(() => null);
      if (body?.folder_path && typeof body.folder_path === "string") {
        folderPath = body.folder_path;
      }
    }
  } catch {
    /* ignore */
  }

  const fastApiUrl = `${FASTAPI_BASE_URL}/api/ingest-folder`;

  try {
    // 1) An FastAPI submitten
    const res = await fetch(fastApiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder_path: folderPath }),
    });

    const backend = await res.json().catch(() => ({}));

    if (!res.ok) {
      return NextResponse.json(
        {
          error: "Backend-Ingestion fehlgeschlagen",
          status: res.status,
          backend,
          sent: { folder_path: folderPath, fastapi_url: fastApiUrl },
        },
        { status: 502 }
      );
    }

    // 2) Inhalte im Literature-Ordner löschen (Ordner bleibt erhalten)
    const deleted = await clearDirectoryContents(folderPath);

    return NextResponse.json(
      {
        message: "Ingestion an Backend übergeben und Literatur-Ordner geleert.",
        folder_path: folderPath,
        deleted_count: deleted.length,
        backend,
      },
      { status: 200 }
    );
  } catch (e: any) {
    return NextResponse.json(
      {
        error: e?.message ?? "Unbekannter Fehler in submit-literature",
        hint:
          "Läuft FastAPI lokal? Stimmt FASTAPI_BASE_URL? Existiert der Ordner public/Literature?",
        sent: { folder_path: folderPath, fastapi_url: fastApiUrl },
      },
      { status: 500 }
    );
  }
}
/**
 * 📄 API: Submit Literature
 *
 * Zweck:
 *  - Ruft dein FastAPI-Backend unter /api/ingest-folder auf
 *  - Übergibt den Pfad zum Ordner public/Literature (oder optional einen anderen Ordner via JSON)
 *  - Löscht anschließend ALLE Inhalte in diesem Ordner (Ordner selbst bleibt bestehen)
 *
 * Nutzung:
 *  - POST /api/submit-literature   → nimmt automatisch public/Literature
 *  - POST /api/submit-literature { "folder_path": "/anderer/pfad" }
 *
 * Voraussetzungen:
 *  - FastAPI läuft lokal auf http://localhost:8000 (oder per FASTAPI_BASE_URL in .env.local angepasst)
 *  - In FastAPI muss der Endpoint /api/ingest-folder verfügbar sein
 *
 * Response:
 *  {
 *    "message": "...",
 *    "folder_path": "...",
 *    "deleted_count": 3,
 *    "backend": {... Antwort vom FastAPI ...}
 *  }
 */