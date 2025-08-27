// src/app/api/upload-literature/route.ts
import { NextResponse } from "next/server";
import path from "path";
import { mkdir, writeFile, access } from "fs/promises";
import { constants as fsConstants } from "fs";
import crypto from "crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Ziel: <projectRoot>/public/Literature
const LITERATURE_DIR = path.join(process.cwd(), "public", "Literature");

function sanitizeFilename(name: string) {
  const cleaned = (name || "file.pdf")
    .replace(/[\u0000-\u001f<>:"/\\|?*\u007f]+/g, "_")
    .replace(/\s+/g, " ")
    .trim();
  return cleaned || `file_${Date.now()}.pdf`;
}

async function ensureDirExists(dir: string) {
  try {
    await access(dir, fsConstants.F_OK);
  } catch {
    await mkdir(dir, { recursive: true });
  }
}

function isPdf(file: File) {
  const n = (file.name || "").toLowerCase();
  const byExt = n.endsWith(".pdf");
  const byMime = (file.type || "").toLowerCase() === "application/pdf";
  return byExt || byMime;
}

async function uniqueTargetPath(filename: string) {
  const base = path.basename(filename, path.extname(filename));
  const ext = path.extname(filename) || ".pdf";
  const stamp = crypto.randomBytes(4).toString("hex");
  return path.join(LITERATURE_DIR, `${base}_${stamp}${ext}`);
}

export async function POST(req: Request) {
  try {
    const ct = req.headers.get("content-type") || "";
    if (!ct.toLowerCase().includes("multipart/form-data")) {
      return NextResponse.json(
        { error: 'Erwarte "multipart/form-data".' },
        { status: 415 }
      );
    }

    const formData = await req.formData();

    const files: File[] = [];
    const single = formData.get("file");
    if (single instanceof File) files.push(single);
    const many = formData.getAll("files");
    for (const f of many) if (f instanceof File) files.push(f);

    if (files.length === 0) {
      return NextResponse.json(
        { error: 'Keine Dateien gefunden. Sende "file" oder "files".' },
        { status: 400 }
      );
    }

    for (const f of files) {
      if (!isPdf(f)) {
        return NextResponse.json(
          { error: `Nur PDFs erlaubt: "${f.name || "unbenannt"}"` },
          { status: 400 }
        );
      }
    }

    await ensureDirExists(LITERATURE_DIR);

    const saved: { originalName: string; savedAs: string; publicUrl: string }[] = [];

    for (const file of files) {
      const original = file.name || "unbenannt.pdf";
      const withExt = original.toLowerCase().endsWith(".pdf") ? original : `${original}.pdf`;
      const clean = sanitizeFilename(withExt);
      const targetPath = await uniqueTargetPath(clean);

      const buf = Buffer.from(await file.arrayBuffer());
      await writeFile(targetPath, buf);

      const publicRel = path
        .relative(path.join(process.cwd(), "public"), targetPath)
        .split(path.sep)
        .join("/");

      saved.push({
        originalName: original,
        savedAs: path.basename(targetPath),
        publicUrl: `/${publicRel}`,
      });
    }

    return NextResponse.json(
      { message: "Upload erfolgreich.", count: saved.length, items: saved },
      { status: 201 }
    );
  } catch (e: any) {
    return NextResponse.json(
      {
        error: e?.message ?? "Unbekannter Fehler",
        hint:
          "Prüfe: Runtime=nodejs, multipart/form-data, lokale Umgebung (kein Edge-only), Dateinamen.",
      },
      { status: 500 }
    );
  }
}

/**
 * 📄 API-Dokumentation: Upload Literature
 *
 * Route: POST /api/upload-literature
 * Runtime: Node.js (kein Edge)
 *
 * Beschreibung:
 *  - Nimmt ein oder mehrere PDF-Dateien entgegen.
 *  - Speichert sie in <projectRoot>/public/Literature (Ordner wird automatisch erstellt).
 *  - Gibt JSON mit Infos zu den gespeicherten Dateien zurück.
 *
 * Erwartetes Request-Format:
 *  Content-Type: multipart/form-data
 *
 * FormData Felder:
 *  - "file": eine einzelne Datei
 *  - oder "files": mehrere Dateien
 *
 * Beispiel mit curl (eine Datei):
 *  curl -X POST http://localhost:3000/api/upload-literature \
 *       -F "file=@/Pfad/zur/datei.pdf"
 *
 * Beispiel mit curl (mehrere Dateien):
 *  curl -X POST http://localhost:3000/api/upload-literature \
 *       -F "files=@/Pfad/eins.pdf" \
 *       -F "files=@/Pfad/zwei.pdf"
 *
 * Antwort (JSON):
 *  {
 *    "message": "Upload erfolgreich.",
 *    "count": 2,
 *    "items": [
 *      {
 *        "originalName": "eins.pdf",
 *        "savedAs": "eins_ab12cd34.pdf",
 *        "publicUrl": "/Literature/eins_ab12cd34.pdf"
 *      },
 *      ...
 *    ]
 *  }
 *
 * Hinweis:
 *  - Nur Dateien mit Endung .pdf oder MIME-Type application/pdf werden akzeptiert.
 *  - Aufrufbar über Browser-Formulare, Fetch API oder Tools wie Postman/curl.
 *  - Hochgeladene Dateien sind sofort unter http://localhost:3000/Literature/... erreichbar.
 */