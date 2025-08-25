"use client";

import * as React from "react";
import Link from "next/link";

export type MetricCardProps = {
  /** Titel der Metrik, z. B. "Conversion Rate" */
  label: string;
  /** Wert der Metrik; Zahlen werden tabellarisch gesetzt */
  value: number | string;
  /** Optional: Ziel-URL. Wenn gesetzt, verhält sich die Kachel wie ein Button/Link */
  href?: string;
  /** Zusätzliche Tailwind-Klassen (optional) */
  className?: string;
  /** Inhalte ausrichten (optional) */
  align?: "start" | "center" | "end";
  /** Optionales Sub-Label, z. B. "Heute" oder "Δ vs. Vortag" */
  sublabel?: string;
};

/**
 * Quadratische Metrik-Kachel mit abgerundeten Ecken und Button‑Like Hover/Active.
 * Nutzt Tailwind CSS-Klassen. Füge Tailwind in deinem Next.js Projekt hinzu
 * oder passe die Klassen nach Bedarf an.
 */
export default function MetricCard({
  label,
  value,
  href,
  className = "",
  align = "center",
  sublabel,
}: MetricCardProps) {
  const alignment =
    align === "start"
      ? "items-start text-left"
      : align === "end"
      ? "items-end text-right"
      : "items-center text-center";

  const content = (
    <div
      className={[
        // Form & Layout
        "aspect-square rounded-2xl border",
        "p-5 flex",
        // Hintergrund & Rahmen + schöner Schatten
        "bg-white border-gray-200 shadow-md hover:shadow-lg",
        // Dark Mode
        "dark:bg-neutral-900 dark:border-neutral-800",
        // Interaktionen: Button-Feeling
        "transition-all duration-200 ease-out",
        "hover:-translate-y-0.5 active:translate-y-0",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/60",
        "cursor-pointer group",
        alignment,
        className,
      ].join(" ")}
      role={href ? "link" : "group"}
      aria-label={`${label}: ${typeof value === "number" ? formatNumber(value) : value}`}
    >
      <div className="m-auto flex flex-col gap-2">
        {/* Label größer & bold */}
        <span className="text-2xl md:text-3xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">
          {label}
        </span>
        {/* Wert kleiner & nicht bold */}
        <span className="text-lg md:text-xl font-normal tabular-nums leading-none text-gray-700 dark:text-gray-300">
          {typeof value === "number" ? formatNumber(value) : value}
        </span>
        {sublabel ? (
          <span className="text-xs text-gray-400 dark:text-gray-500">{sublabel}</span>
        ) : null}
      </div>
      {/* Hover-Accent Border */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl ring-0 ring-transparent group-hover:ring-1 group-hover:ring-indigo-500/40" />
    </div>
  );

  // Wenn href gesetzt ist, als Link rendern, sonst als statisches Element
  return href ? (
    <Link href={href} className="relative block">
      {content}
    </Link>
  ) : (
    <div className="relative">{content}</div>
  );
}

function formatNumber(n: number) {
  try {
    return new Intl.NumberFormat(undefined, {
      maximumFractionDigits: 2,
    }).format(n);
  } catch {
    return String(n);
  }
}

/**
 * Beispiel-Nutzung:
 *
 * <MetricCard label="Umsatz" value={12345.67} sublabel="Heute" href="/metrics/revenue" />
 * <MetricCard label="Aktive Nutzer" value={842} align="start" href="/users/active" />
 * <MetricCard label="Conversion Rate" value="3.9%" align="end" /> // ohne Link
 */
