// src/app/results/page.tsx
import { redirect } from "next/navigation";
import { headers } from "next/headers";
import Link from "next/link";

type MetricEntry = { value: unknown; llm_response?: string; sources?: string[] };
type LastRunResponse =
  | { exists: true; data: any; meta: { ticker: string | null; savedAt: string | null }; path: string }
  | { exists: false; data: null; meta: { ticker: null; savedAt: null }; path: string };

function prettyLabel(k: string) {
  const s = k.replace(/[_-]+/g, " ").trim();
  return s.charAt(0).toUpperCase() + s.slice(1);
}
function slugify(k: string) {
  return k.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
}
function formatValue(v: unknown) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return Number.isFinite(v) ? v.toLocaleString("de-DE") : String(v);
  if (typeof v === "string") return v.length > 120 ? v.slice(0, 117) + "…" : v;
  const s = JSON.stringify(v);
  return s.length > 120 ? s.slice(0, 117) + "…" : s;
}
function normalizeMetrics(data: any): { key: string; label: string; slug: string; entry: MetricEntry }[] {
  const results: Record<string, MetricEntry> =
    (data?.results as Record<string, MetricEntry>) || (data as Record<string, MetricEntry>) || {};
  const pairs = Object.entries(results).filter(([, v]) => v && typeof v === "object" && "value" in (v as any));
  return pairs.slice(0, 8).map(([key, entry]) => ({
    key,
    label: prettyLabel(key),
    slug: slugify(key),
    entry: entry as MetricEntry,
  }));
}

function getBaseUrl() {
  const h = headers();
  const proto = h.get("x-forwarded-proto") ?? "http";
  const host = h.get("x-forwarded-host") ?? h.get("host");
  if (!host) return process.env.NEXT_PUBLIC_BASE_URL ?? "http://localhost:3000";
  return `${proto}://${host}`;
}

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function ResultsPage() {
  const baseUrl = getBaseUrl();
  const res = await fetch(`${baseUrl}/api/last-run`, { cache: "no-store" });
  const lastRun = (await res.json()) as LastRunResponse;

  if (!lastRun.exists || !lastRun.data) redirect("/");

  const metrics = normalizeMetrics(lastRun.data);
  if (metrics.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-slate-200">
        <p className="text-sm">Keine Metriken gefunden. Bitte eine neue Analyse starten.</p>
        <div className="mt-4">
          <Link href="/" className="rounded-lg px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700">
            Zur Landing
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
        <span>
          Ticker: <span className="font-mono text-slate-100">{lastRun.meta.ticker ?? "—"}</span>
        </span>
        <span className="opacity-60">•</span>
        <span>
          Stand:{" "}
          <span className="font-mono text-slate-100">
            {lastRun.meta.savedAt ? new Date(lastRun.meta.savedAt).toLocaleString("de-DE") : "—"}
          </span>
        </span>
      </div>

      <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {metrics.map(({ key, label, slug, entry }) => (
          <li
            key={key}
            className="group rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg ring-1 ring-white/10 transition hover:shadow-xl hover:bg-white/10"
          >
            <div className="flex items-start justify-between gap-3">
              <h3 className="text-base font-semibold text-white">{label}</h3>
              <Link
                href={`/results/${slug}`}
                className="text-xs text-slate-300 hover:text-white underline underline-offset-4"
              >
                Details
              </Link>
            </div>

            <div className="mt-4">
              <p className="text-3xl font-semibold text-white tabular-nums break-words">
                {formatValue(entry.value)}
              </p>
            </div>

            <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
              <span>Quellen: {Array.isArray(entry.sources) ? entry.sources.length : 0}</span>
              <span className="opacity-70">LLM: {entry.llm_response ? "vorhanden" : "—"}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
