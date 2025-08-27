// src/lib/metrics.ts
export function slugify(k: string) {
  return k.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
}
export function prettyLabel(k: string) {
  const s = k.replace(/[_-]+/g, " ").trim();
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export type MetricEntry = {
  value: unknown;
  llm_response?: string;
  sources?: string[];
};

// Versucht, aus dem last-run Payload die Metrik zum Slug zu finden.
export function getMetricFromLastRun(
  data: any,
  slug: string
): { key: string; label: string; entry: MetricEntry } | null {
  const results: Record<string, MetricEntry> =
    (data?.results as Record<string, MetricEntry>) ||
    (data as Record<string, MetricEntry>) ||
    {};

  for (const [key, entry] of Object.entries(results)) {
    if (slugify(key) === slug) {
      return { key, label: prettyLabel(key), entry: entry as MetricEntry };
    }
  }
  return null;
}

export function toHref(src: string) {
  if (!src) return "#";
  if (/^https?:\/\//i.test(src)) return src;
  return src.startsWith("/") ? src : `/${src}`;
}
