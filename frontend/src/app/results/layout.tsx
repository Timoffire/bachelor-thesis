// src/app/results/layout.tsx
import Link from "next/link";

export default function ResultsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-[calc(100vh-3rem)] bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl md:text-3xl font-semibold text-white">Analyse-Ergebnisse</h1>
            <p className="mt-1 text-sm text-slate-300">Übersicht der 8 Metriken mit aktuellem Wert.</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="rounded-xl px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700"
              title="Zur Landing – neue Analyse starten"
            >
              Neue Analyse
            </Link>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}
