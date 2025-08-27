// src/app/results/[metric]/page.tsx
import { headers } from "next/headers";
import { redirect, notFound } from "next/navigation";
import Link from "next/link";
import CopyButton from "@/components/ui/CopyButton";
import { getMetricFromLastRun, toHref } from "@/lib/metrics";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const dynamic = "force-dynamic";
export const revalidate = 0;

function getBaseUrl() {
  const h = headers();
  const proto = h.get("x-forwarded-proto") ?? "http";
  const host = h.get("x-forwarded-host") ?? h.get("host");
  return host ? `${proto}://${host}` : process.env.NEXT_PUBLIC_BASE_URL ?? "http://localhost:3000";
}

export default async function MetricDetailPage({ params }: { params: { metric: string } }) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/last-run`, { cache: "no-store" });
  const last = await res.json();

  if (!last?.exists || !last?.data) redirect("/");

  const found = getMetricFromLastRun(last.data, params.metric);
  if (!found) notFound();

  const { label, entry } = found;
  const llmText = (entry.llm_response ?? "").toString();

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 ring-1 ring-white/10 text-slate-100">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{label}</h1>
          <p className="mt-1 text-sm text-slate-300">
            Aktueller Wert:{" "}
            <span className="font-mono text-slate-100">
              {entry?.value === null || entry?.value === undefined ? "—" : String(entry.value)}
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/results" className="rounded-lg px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20">
            ← Zur Übersicht
          </Link>
          <Link href="/" className="rounded-lg px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20">
            Neue Analyse
          </Link>
        </div>
      </div>

      {/* LLM Output als Markdown */}
<section className="mt-6">
  <div className="mb-2 flex items-center justify-between">
    <h2 className="text-sm font-semibold text-slate-200">LLM-Output</h2>
    {llmText && <CopyButton text={llmText} />}
  </div>

  <article className="rounded-2xl border border-white/10 bg-black/30 p-4">
    {/* Wrapper bekommt die Styles, NICHT ReactMarkdown selbst */}
    <div className="prose prose-invert max-w-none prose-headings:mt-4 prose-p:leading-7 prose-code:text-slate-200">
      <ReactMarkdown remarkPlugins={[remarkGfm]}
        components={{
          a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noreferrer" className="underline underline-offset-4" />
          ),
          code: ({ inline, className, children, ...props }) =>
            inline ? (
              <code className="px-1 py-0.5 rounded bg-white/10" {...props}>{children}</code>
            ) : (
              <pre className="rounded-xl bg-black/50 p-3 overflow-auto">
                <code className={className} {...props}>{children}</code>
              </pre>
            ),
          table: ({ children }) => (
            <div className="overflow-x-auto">
              <table className="table-auto border-collapse">{children}</table>
            </div>
          ),
        }}
      >
        {llmText || "Kein LLM-Output vorhanden."}
      </ReactMarkdown>
    </div>
  </article>
</section>


      {/* Quellen */}
      <section className="mt-6">
        <h2 className="text-sm font-semibold text-slate-200 mb-2">Quellen</h2>
        {Array.isArray(entry.sources) && entry.sources.length > 0 ? (
          <ul className="space-y-1 text-sm">
            {entry.sources.map((s, i) => (
              <li key={`${s}-${i}`} className="truncate">
                <a href={toHref(s)} target="_blank" rel="noreferrer" className="underline underline-offset-4 hover:text-white">
                  {s}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-300 text-sm">Keine Quellen angegeben.</p>
        )}
      </section>
    </div>
  );
}
