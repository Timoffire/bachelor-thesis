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

/**
 * Split Markdown by ATX headings (# ... ######) into sections.
 * Each section has: level (1-6), title (string), body (markdown without its heading).
 * If no heading exists, return a single section with title "Output".
 */
function splitMarkdownIntoSections(md: string): Array<{ level: number; title: string; body: string }> {
  const text = md?.trim() ?? "";
  if (!text) return [];

  // Normalize CRLF
  const src = text.replace(/\r\n/g, "\n");

  const headingRegex = /^(\#{1,6})\s+(.+?)\s*#*\s*$/gm;
  const matches: Array<{ level: number; title: string; start: number; end?: number }> = [];

  let m: RegExpExecArray | null;
  while ((m = headingRegex.exec(src))) {
    matches.push({ level: m[1].length, title: m[2], start: m.index });
  }
  if (matches.length === 0) {
    return [{ level: 2, title: "Output", body: src }];
  }
  // compute section body ranges
  for (let i = 0; i < matches.length; i++) {
    matches[i].end = i + 1 < matches.length ? matches[i + 1].start : src.length;
  }
  return matches.map((h) => {
    // slice from after the heading line to end
    const lineEnd = src.indexOf("\n", h.start);
    const bodyRaw = lineEnd >= 0 ? src.slice(lineEnd + 1, h.end) : "";
    return { level: h.level, title: h.title.trim(), body: bodyRaw.trim() };
  });
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
  const sections = splitMarkdownIntoSections(llmText);

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 ring-1 ring-white/10 text-slate-100">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{label}</h1>
          <p className="mt-1 text-sm text-slate-300">
            Current value:{" "}
            <span className="font-mono text-slate-100">
              {entry?.value === null || entry?.value === undefined ? "—" : String(entry.value)}
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/results" className="rounded-lg px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20">
            ← Back to overview
          </Link>
          <Link href="/" className="rounded-lg px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20">
            New analysis
          </Link>
        </div>
      </div>

      {/* LLM output */}
      <section className="mt-6">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200">LLM output</h2>
          {llmText && <CopyButton text={llmText} />}
        </div>

        {/* Render each heading + body as its own section with a text field */}
        <div className="space-y-5">
          {sections.length > 0 ? (
            sections.map((sec, idx) => (
              <div key={`${sec.title}-${idx}`}>
                {/* Heading */}
                <h3
                  className={[
                    "text-sm font-semibold text-slate-200",
                    // subtle hierarchy by level, but keep compact
                    sec.level <= 2 ? "text-base" : "",
                  ].join(" ")}
                >
                  {sec.title}
                </h3>

                {/* Text field */}
                <article className="mt-2 rounded-xl border border-white/15 bg-black/40 p-4 shadow-sm">
                  <div
                    className={[
                      "prose prose-invert max-w-none",
                      "prose-p:leading-7",
                      "prose-headings:mt-4",
                      "prose-code:text-slate-200",
                      "prose-ul:mt-3 prose-ul:space-y-2 prose-ol:mt-3 prose-ol:space-y-2",
                    ].join(" ")}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        a: ({ node, ...props }) => (
                          <a {...props} target="_blank" rel="noreferrer" className="underline underline-offset-4" />
                        ),
                        code: ({ inline, className, children, ...props }) =>
                          inline ? (
                            <code className="px-1 py-0.5 rounded bg-white/10" {...props}>
                              {children}
                            </code>
                          ) : (
                            <pre className="rounded-xl bg-black/50 p-3 overflow-auto">
                              <code className={className} {...props}>
                                {children}
                              </code>
                            </pre>
                          ),
                        table: ({ children }) => (
                          <div className="overflow-x-auto">
                            <table className="table-auto border-collapse">{children}</table>
                          </div>
                        ),
                        // clearer distinction for bolded labels within text
                        strong: ({ children, ...props }) => (
                          <strong
                            {...props}
                            className="font-semibold text-slate-100 bg-white/10 rounded px-1.5 py-0.5 mr-1"
                          >
                            {children}
                          </strong>
                        ),
                        li: ({ children, ...props }) => (
                          <li {...props} className="leading-7 marker:text-indigo-300 marker:opacity-80">
                            {children}
                          </li>
                        ),
                        // prevent nested headings inside the text field from looking like top-level titles
                        h1: ({ children }) => <p className="font-semibold mt-3">{children}</p>,
                        h2: ({ children }) => <p className="font-semibold mt-3">{children}</p>,
                        h3: ({ children }) => <p className="font-semibold mt-3">{children}</p>,
                        h4: ({ children }) => <p className="font-semibold mt-3">{children}</p>,
                        h5: ({ children }) => <p className="font-semibold mt-3">{children}</p>,
                        h6: ({ children }) => <p className="font-semibold mt-3">{children}</p>,
                      }}
                    >
                      {sec.body || "_No content._"}
                    </ReactMarkdown>
                  </div>
                </article>
              </div>
            ))
          ) : (
            <article className="rounded-xl border border-white/15 bg-black/40 p-4 shadow-sm">
              <p className="text-sm text-slate-300">No LLM output available.</p>
            </article>
          )}
        </div>
      </section>

      {/* Sources */}
      <section className="mt-6">
        <h2 className="text-sm font-semibold text-slate-200 mb-2">Sources</h2>
        {Array.isArray(entry.sources) && entry.sources.length > 0 ? (
          <ul className="space-y-1 text-sm">
            {entry.sources.map((s, i) => (
              <li key={`${s}-${i}`} className="truncate">
                <a
                  href={toHref(s)}
                  target="_blank"
                  rel="noreferrer"
                  className="underline underline-offset-4 hover:text-white"
                >
                  {s}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-300 text-sm">No sources provided.</p>
        )}
      </section>
    </div>
  );
}
