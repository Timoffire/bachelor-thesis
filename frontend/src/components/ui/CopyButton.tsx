// src/components/ui/CopyButton.tsx
"use client";

import { useState } from "react";

export default function CopyButton({ text, className = "" }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  async function onCopy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {}
  }
  return (
    <button
      onClick={onCopy}
      className={`rounded-lg px-3 py-1.5 text-xs bg-white/10 text-white hover:bg-white/20 ${className}`}
      title="LLM-Output kopieren"
    >
      {copied ? "Kopiert ✓" : "Kopieren"}
    </button>
  );
}
