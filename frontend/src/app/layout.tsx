// src/app/layout.tsx
import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Context-Aware RAG-System for Interpretable Stock Analysis",
  description: "Landing → Ergebnisse → Metrik-Details",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de" className="h-full">
      <body className="h-full min-h-screen antialiased">
        {/* Transluzenz-Navbar: von überall zurück nach Hause */}
        <nav className="sticky top-0 z-50 border-b border-white/10 bg-black/30 backdrop-blur-md">
          <div className="mx-auto max-w-7xl px-6 py-3 flex items-center justify-between">
            <Link href="/" className="font-semibold text-white hover:opacity-90">
              RAG<span className="opacity-70">·Home</span>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/results" className="text-sm text-slate-200 hover:text-white">
                Results
              </Link>
            </div>
          </div>
        </nav>

        {/* Wichtig: kein Container hier – Seiten (z. B. Landing) übernehmen ihr eigenes Layout */}
        <main className="min-h-[calc(100vh-3rem)]">{children}</main>
      </body>
    </html>
  );
}
