// src/app/results/page.tsx
import { redirect } from "next/navigation";
import { headers } from "next/headers";
import Link from "next/link";

type MetricEntry = { value: unknown; llm_response?: string; sources?: string[] };
type LastRunResponse =
  | { exists: true; data: any; meta: { ticker: string | null; savedAt: string | null }; path: string }
  | { exists: false; data: null; meta: { ticker: null; savedAt: null }; path: string };

// ---------- Label + Formatting Config ----------

const LABEL_OVERRIDES: Record<string, string> = {
  eps: "Earnings per Share (EPS)",
  pe_ratio: "Price / Earnings (P/E Ratio)",
  roa: "Return on Assets (ROA)",
  pb_ratio: "Price / Book (P/B Ratio)",
  roe: "Return on Equity (ROE)",
  debt_to_equity: "Debt-to-Equity",
  market_cap: "Market Capitalization",
  price_to_sales: "Price / Sales (P/S Ratio)",
};

const FORMATTERS: Record<string, (v: unknown) => string> = {
  eps: (v) => formatNumber(v, { maxFractionDigits: 2 }),
  pe_ratio: (v) => formatNumber(v, { maxFractionDigits: 2 }),
  pb_ratio: (v) => formatNumber(v, { maxFractionDigits: 2 }),
  price_to_sales: (v) => formatNumber(v, { maxFractionDigits: 2 }),

  roa: (v) => formatPercent(v),
  roe: (v) => formatPercent(v),
  debt_to_equity: (v) => formatPercent(v), // 👈 jetzt als Prozent

  market_cap: (v) => formatMoney(v, { compact: true }),
};

// ---------- Helpers ----------

function titleCaseFromKey(k: string) {
  // base fallback if no override
  const s = k.replace(/[_-]+/g, " ").trim();
  return s
    .split(" ")
    .map((w) => {
      const u = w.toUpperCase();
      if (["EPS", "PE", "P/E", "PS", "ROE", "ROA", "TTM", "FCF", "EBITDA"].includes(u)) return u;
      return w.charAt(0).toUpperCase() + w.slice(1);
    })
    .join(" ");
}

function prettyLabelFromSlug(slug: string) {
  if (LABEL_OVERRIDES[slug]) return LABEL_OVERRIDES[slug];
  return titleCaseFromKey(slug);
}

function slugify(k: string) {
  return k.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
}

// Formatting primitives
function formatNumber(v: unknown, opts?: { maxFractionDigits?: number; compact?: boolean }) {
  if (typeof v !== "number" || !Number.isFinite(v)) return String(v ?? "—");
  const { maxFractionDigits = 2, compact = false } = opts ?? {};
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: maxFractionDigits,
    notation: compact ? "compact" : "standard",
  }).format(v);
}

function formatMoney(v: unknown, opts?: { currency?: string; compact?: boolean }) {
  if (typeof v !== "number" || !Number.isFinite(v)) return String(v ?? "—");
  const currency = opts?.currency ?? "USD";
  const compact = opts?.compact ?? false;
  // For very large numbers, compact currency helps (e.g., $1.2T)
  if (compact) {
    // emulate compact currency with symbol + compact number
    const abs = Math.abs(v);
    const compactStr = new Intl.NumberFormat("en-US", {
      maximumFractionDigits: abs < 1 ? 4 : 2,
      notation: "compact",
    }).format(v);
    const symbol = currencySymbol(currency);
    return `${symbol}${compactStr}`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: Math.abs(v) < 1 ? 4 : 2,
  }).format(v);
}

function currencySymbol(c: string) {
  // minimal mapping; extend as needed
  switch (c) {
    case "USD":
      return "$";
    case "EUR":
      return "€";
    case "GBP":
      return "£";
    case "JPY":
      return "¥";
    default:
      return "";
  }
}

function formatPercent(v: unknown) {
  if (typeof v !== "number" || !Number.isFinite(v)) return String(v ?? "—");
  // If value is 0..1, treat as ratio; otherwise assume already percent
  const asRatio = Math.abs(v) <= 1.0001;
  const pct = asRatio ? v * 100 : v;
  const digits = Math.abs(pct) < 1 ? 2 : Math.abs(pct) < 10 ? 1 : 0;
  return `${pct.toFixed(digits)}%`;
}

function tryFormatDateString(s: string) {
  // Accept ISO-ish strings
  const t = Date.parse(s);
  if (Number.isNaN(t)) return null;
  return new Date(t).toLocaleString("en-US");
}

function truncateJSON(v: unknown, max = 120) {
  const s = JSON.stringify(v);
  return s.length > max ? s.slice(0, max - 1) + "…" : s;
}

// Smart fallback when no specific formatter is found
function formatValueSmart(v: unknown, keySlug: string) {
  if (v === null || v === undefined) return "—";

  // If a specific formatter exists, use it
  const f = FORMATTERS[keySlug];
  if (f) return f(v);

  // Heuristics
  if (typeof v === "number" && Number.isFinite(v)) {
    const k = keySlug;

    // percentage-like keys
    if (/(percent|percentage|margin|growth|yoy|qoq|rate|yield)/i.test(k)) {
      return formatPercent(v);
    }

    // money-like keys
    if (/(price|revenue|income|profit|cap|cash|debt|ebit|ebitda|valuation|sales|cost|opex|fcf|dividend)/i.test(k)) {
      return formatMoney(v, { compact: Math.abs(v) >= 1_000_000 });
    }

    // counts/volumes
    if (/(count|volume|shares|documents|items|contracts|trades)/i.test(k)) {
      return formatNumber(v, { compact: Math.abs(v) >= 10_000 });
    }

    // default number
    return formatNumber(v, { maxFractionDigits: Math.abs(v) < 1 ? 4 : 2 });
  }

  if (typeof v === "string") {
    const maybeDate = tryFormatDateString(v);
    if (maybeDate) return maybeDate;
    return v.length > 120 ? v.slice(0, 117) + "…" : v;
  }

  // arrays/objects
  return truncateJSON(v);
}

// ---------- Metric normalization ----------

function normalizeMetrics(data: any): { key: string; label: string; slug: string; entry: MetricEntry }[] {
  const results: Record<string, MetricEntry> =
    (data?.results as Record<string, MetricEntry>) || (data as Record<string, MetricEntry>) || {};
  const pairs = Object.entries(results).filter(([, v]) => v && typeof v === "object" && "value" in (v as any));

  return pairs.slice(0, 8).map(([key, entry]) => {
    const slug = slugify(key);
    return {
      key,
      label: prettyLabelFromSlug(slug),
      slug,
      entry: entry as MetricEntry,
    };
  });
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
        <p className="text-sm">No metrics found. Please start a new analysis.</p>
        <div className="mt-4">
          <Link href="/" className="rounded-lg px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700">
            Back to landing
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
          Saved at:{" "}
          <span className="font-mono text-slate-100">
            {lastRun.meta.savedAt ? new Date(lastRun.meta.savedAt).toLocaleString("en-US") : "—"}
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
                {formatValueSmart((entry as MetricEntry).value, slug)}
              </p>
            </div>

            <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
              <span>Sources: {Array.isArray(entry.sources) ? entry.sources.length : 0}</span>
              <span className="opacity-70">LLM: {entry.llm_response ? "available" : "—"}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
