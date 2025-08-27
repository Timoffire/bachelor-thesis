"use client";

/**
 * 🎯 Landingpage (Split-Layout) – mit nebeneinander liegenden PDF-Buttons
 *
 * Links oben:
 *  - "PDFs auswählen" (öffnet File Dialog, speichert Auswahl lokal)
 *  - "PDF hochladen"  (aktiv NUR wenn links gewählt wurde; macht Upload -> Submit an Backend)
 *    → nach Erfolg wird RUN freigeschaltet
 *
 * Links unten:
 *  - "DB zurücksetzen" (setzt Collection zurück und sperrt RUN wieder)
 *
 * Rechts:
 *  - Ticker eingeben + "Analyse starten"
 *  - RUN ist deaktiviert, bis Upload+Submit erfolgreich war ODER bereits ein Last-Run existiert
 *  - Während run() aktiv ist: volle Page gesperrt (Overlay + Spinner)
 */

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type Jsonish = any;

export default function LandingPage() {
  const router = useRouter();

  // Blocker während run()
  const [blocking, setBlocking] = useState(false);

  // Gating für RUN
  const [ingestionReady, setIngestionReady] = useState(false);

  // Files (nur ausgewählt, noch nicht hochgeladen)
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[] | null>(null);

  // Upload/Submit Status
  const [busyUpload, setBusyUpload] = useState(false);
  const [uploadResp, setUploadResp] = useState<Jsonish | null>(null);
  const [submitResp, setSubmitResp] = useState<Jsonish | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // DB Reset
  const [resetting, setResetting] = useState(false);
  const [resetResp, setResetResp] = useState<Jsonish | null>(null);

  // Run
  const [ticker, setTicker] = useState("AAPL");
  const [runError, setRunError] = useState<string | null>(null);

  // Beim Laden prüfen, ob schon ein Last-Run existiert → dann RUN freigeben
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/last-run", { cache: "no-store" });
        const data = await res.json();
        if (data?.exists) setIngestionReady(true);
      } catch {
        // optional: ignorieren
      }
    })();
  }, []);

  function onChooseFiles(files: FileList | null) {
    if (!files || files.length === 0) {
      setSelectedFiles(null);
      return;
    }
    setSelectedFiles(Array.from(files));
    setUploadResp(null);
    setSubmitResp(null);
    setUploadError(null);
  }

  async function onUploadAndSubmit() {
    if (!selectedFiles || selectedFiles.length === 0) return;

    setBusyUpload(true);
    setUploadError(null);
    setUploadResp(null);
    setSubmitResp(null);

    try {
      // 1) Upload nach /api/upload-literature
      const fd = new FormData();
      for (const f of selectedFiles) fd.append("files", f);
      const upRes = await fetch("/api/upload-literature", { method: "POST", body: fd });
      const upJson = await upRes.json();
      setUploadResp(upJson);
      if (!upRes.ok || upJson?.error) {
        throw new Error(upJson?.error ?? `Upload fehlgeschlagen (HTTP ${upRes.status})`);
      }

      // 2) Direkt an Backend submitten & Ordner leeren
      const subRes = await fetch("/api/submit-literature", { method: "POST" });
      const subJson = await subRes.json();
      setSubmitResp(subJson);
      if (!subRes.ok || subJson?.error) {
        throw new Error(subJson?.error ?? `Submit fehlgeschlagen (HTTP ${subRes.status})`);
      }

      // ✔️ Erfolgreich → RUN freigeben
      setIngestionReady(true);
      // Auswahl zurücksetzen
      setSelectedFiles(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (e: any) {
      setUploadError(e?.message ?? "Unbekannter Fehler beim Upload/Submit");
      setIngestionReady(false);
    } finally {
      setBusyUpload(false);
    }
  }

  async function handleResetDb() {
    setResetting(true);
    setResetResp(null);
    try {
      const res = await fetch("/api/reset-collection", { method: "POST" });
      const data = await res.json();
      setResetResp(data);
      // Nach Reset RUN wieder sperren
      setIngestionReady(false);
    } catch (e: any) {
      setResetResp({ error: e?.message ?? "Unbekannter Fehler beim Reset" });
    } finally {
      setResetting(false);
    }
  }

  async function handleRun() {
    if (!ingestionReady) {
      setRunError("Bitte zuerst PDFs auswählen & hochladen.");
      return;
    }
    if (!ticker.trim()) {
      setRunError("Bitte einen Ticker eingeben (z. B. AAPL).");
      return;
    }

    setRunError(null);
    setBlocking(true);

    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: ticker.trim() }),
      });
      const data = await res.json();

      if (!res.ok || data?.error) {
        setRunError(data?.error ?? `Fehler: HTTP ${res.status}`);
        setBlocking(false);
        return;
      }

      router.push("/results");
    } catch (e: any) {
      setRunError(e?.message ?? "Unbekannter Fehler beim Run");
      setBlocking(false);
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
      {/* dekorativer Hintergrund */}
      <div className="pointer-events-none absolute -top-24 -left-24 h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 -right-24 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-6 py-10">
        {/* Headline */}
        <header className="mb-8 text-center">
          <h1 className="text-3xl md:text-4xl font-semibold text-white tracking-tight">
            RAG Analyseplattform
          </h1>
          <p className="mt-2 text-slate-300">
            Links: Literatur managen · Rechts: Analyse starten
          </p>
        </header>

        {/* Hauptlayout: exakt in der Mitte geteilt */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
          {/* Linke Spalte (oben/unten) */}
          <div className="flex flex-col gap-6">
            {/* Oben: PDFs auswählen & hochladen (nebeneinander) */}
            <section className="flex-1 rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-lg ring-1 ring-white/10 p-6 text-slate-100">
              <h2 className="text-lg font-semibold">Literatur hochladen & submitten</h2>
              <p className="mt-1 text-sm text-slate-300">
                1) PDFs auswählen → 2) PDF hochladen (Upload & Submit ans Backend).
              </p>

              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf,.pdf"
                multiple
                hidden
                onChange={(e) => onChooseFiles(e.target.files)}
                disabled={blocking}
              />

              <div className="mt-6 flex flex-wrap items-center gap-3">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-60 transition"
                  disabled={busyUpload || resetting || blocking}
                >
                  PDFs auswählen
                </button>

                <button
                  onClick={onUploadAndSubmit}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60 transition"
                  disabled={!selectedFiles || selectedFiles.length === 0 || busyUpload || resetting || blocking}
                  title={!selectedFiles || selectedFiles.length === 0 ? "Bitte zuerst PDFs auswählen" : "PDF hochladen & submitten"}
                >
                  {busyUpload ? (
                    <>
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/70 border-t-transparent" />
                      Verarbeite…
                    </>
                  ) : (
                    "PDF hochladen"
                  )}
                </button>

                {/* Info zur Auswahl */}
                <span className="text-xs text-slate-300">
                  {selectedFiles && selectedFiles.length > 0
                    ? `${selectedFiles.length} Datei(en) ausgewählt`
                    : "Keine Dateien ausgewählt"}
                </span>
              </div>

              {uploadError && <p className="mt-3 text-sm text-rose-400">Fehler: {uploadError}</p>}

              {(uploadResp || submitResp) && (
                <details className="mt-3 text-sm">
                  <summary className="cursor-pointer select-none">Details</summary>
                  {uploadResp && (
                    <pre className="mt-2 max-h-40 overflow-auto rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-slate-200">
                      <b>Upload Response:</b>{"\n"}{JSON.stringify(uploadResp, null, 2)}
                    </pre>
                  )}
                  {submitResp && (
                    <pre className="mt-2 max-h-40 overflow-auto rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-slate-200">
                      <b>Submit Response:</b>{"\n"}{JSON.stringify(submitResp, null, 2)}
                    </pre>
                  )}
                </details>
              )}
            </section>

            {/* Unten: DB zurücksetzen */}
            <section className="flex-1 rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-lg ring-1 ring-white/10 p-6 text-slate-100">
              <h2 className="text-lg font-semibold">DB zurücksetzen</h2>
              <p className="mt-1 text-sm text-slate-300">Löscht die aktuelle Collection deiner Vektor-DB.</p>

              <div className="mt-6">
                <button
                  onClick={handleResetDb}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 bg-rose-600 text-white hover:bg-rose-700 disabled:opacity-60 transition"
                  disabled={resetting || busyUpload || blocking}
                >
                  {resetting ? "Setze zurück…" : "Collection löschen"}
                </button>
              </div>

              {resetResp && (
                <pre className="mt-4 max-h-48 overflow-auto rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-slate-200">
                  {JSON.stringify(resetResp, null, 2)}
                </pre>
              )}
            </section>
          </div>

          {/* Rechte Spalte: Run */}
          <section className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-lg ring-1 ring-white/10 p-6 text-slate-100 flex flex-col">
            <h2 className="text-lg font-semibold">Analyse starten</h2>
            <p className="mt-1 text-sm text-slate-300">
              Ticker eingeben und Run ausführen. Run ist erst verfügbar, nachdem PDFs hochgeladen & submit wurden
              {ingestionReady ? " ✅" : " ⛔"}.
            </p>

            <label htmlFor="ticker" className="mt-6 text-sm text-slate-200">
              Ticker
            </label>
            <input
              id="ticker"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="z. B. AAPL"
              className="mt-2 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-slate-100 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={blocking}
            />

            {!ingestionReady && (
              <p className="mt-2 text-xs text-amber-300">
                Bitte zuerst „PDFs auswählen“ und dann „PDF hochladen“ ausführen.
              </p>
            )}
            {runError && <p className="mt-2 text-sm text-rose-400">{runError}</p>}

            <div className="mt-auto pt-6">
              <button
                onClick={handleRun}
                className="w-full rounded-2xl px-5 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 text-white hover:from-indigo-500 hover:to-blue-500 disabled:opacity-60 transition"
                disabled={blocking || !ingestionReady}
                title={!ingestionReady ? "Noch nicht bereit – bitte PDFs hochladen" : "Analyse starten"}
              >
                Analyse starten
              </button>
            </div>
          </section>
        </div>
      </div>

      {/* Vollflächiges Overlay beim Run */}
      {blocking && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 backdrop-blur-sm" aria-busy="true">
          <div className="flex flex-col items-center gap-3">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-indigo-400 border-t-transparent" />
            <p className="text-slate-100">Analyse läuft… bitte warten</p>
          </div>
        </div>
      )}
    </div>
  );
}
