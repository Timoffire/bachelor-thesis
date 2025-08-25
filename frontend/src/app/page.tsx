"use client";

import { useRouter } from "next/navigation";
import MetricsGrid8 from "@/components/Analysis/MetricsGrid8";
import GradientButton from "@/components/Analysis/GradientButton";
import TextWindow from "@/components/Analysis/TextWindow";

export default function Page() {
  const router = useRouter();

  return (
    <div className="space-y-8">
      {/* 8er Grid */}
      <MetricsGrid8
        items={[
          { label: "Umsatz", value: 12345.67, sublabel: "Heute", href: "/metrics/revenue", size: "lg" },
          { label: "Nutzer", value: 842 },
          { label: "CR", value: "3.9%", href: "/metrics/cr" },
          { label: "MRR", value: "€ 12.4k" },
          { label: "Tickets", value: 31 },
          { label: "DAU", value: 512 },
          { label: "Churn", value: "1.2%" },
          { label: "NPS", value: 47 },
        ]}
      />

      {/* Back Button */}
      <div className="flex justify-center">
        <GradientButton size="md" onClick={() => router.back()}>
          Back
        </GradientButton>
      </div>

      {/* TextWindow */}
      <TextWindow text="Hier könnte deine ausführlichere Beschreibung, Analyse oder ein langer Absatz erscheinen. Das Fenster bleibt 16:9 und zeigt den Text schön lesbar in der Mitte an." />
    </div>
  );
}
