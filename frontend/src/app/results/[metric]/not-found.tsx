// src/app/results/[metric]/not-found.tsx
import Link from "next/link";

export default function NotFoundMetric() {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-slate-200">
      <p className="text-sm">Diese Metrik wurde nicht gefunden.</p>
      <div className="mt-4 flex gap-2">
        <Link href="/results" className="rounded-lg px-4 py-2 bg-white/10 hover:bg-white/20 text-white">
          Zur Übersicht
        </Link>
        <Link href="/" className="rounded-lg px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white">
          Neue Analyse
        </Link>
      </div>
    </div>
  );
}
