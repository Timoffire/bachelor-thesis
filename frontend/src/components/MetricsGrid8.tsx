"use client";

import * as React from "react";
import MetricCard, { type MetricCardProps } from "./MetricCard";

export type MetricItem = Omit<MetricCardProps, "className"> & {
  /** Optional: zusätzliche Klassen für einzelne Cards */
  className?: string;
};

export type MetricsGrid8Props = {
  /** Liste der Metriken (nur die ersten 8 werden angezeigt) */
  items: MetricItem[];
  /** Abstand & Außenklassen fürs Grid */
  className?: string;
};

const cn = (...xs: Array<string | undefined>) => xs.filter(Boolean).join(" ");

/**
 * Grid-Komponente für 8 MetricCards, 4 pro Reihe (ab md-Breakpoint).
 * - Mobil 1 Spalte, ab sm 2, ab md 4 Spalten
 * - Nimmt bis zu 8 Items, zusätzliche werden ignoriert
 */
export default function MetricsGrid8({ items, className }: MetricsGrid8Props) {
  const eight = items.slice(0, 8);

  return (
    <div className={cn("grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6", className)}>
      {eight.map((item, i) => (
        <MetricCard
          key={i}
          {...item}
          // volle Breite im Grid + optional eigene Klassen
          className={cn("w-full", item.className)}
        />
      ))}
    </div>
  );
}

/**
 * Beispiel-Nutzung:
 *
 * <MetricsGrid8
 *   items={[
 *     { label: "Umsatz", value: 12345.67, sublabel: "Heute", href: "/metrics/revenue", size: "lg" },
 *     { label: "Nutzer", value: 842 },
 *     { label: "CR", value: "3.9%", href: "/metrics/cr" },
 *     { label: "MRR", value: "€ 12.4k" },
 *     { label: "Tickets", value: 31 },
 *     { label: "DAU", value: 512 },
 *     { label: "Churn", value: "1.2%" },
 *     { label: "NPS", value: 47 },
 *   ]}
 * />
 */
