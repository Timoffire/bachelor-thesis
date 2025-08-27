"use client";

import * as React from "react";

export type TextWindowProps = {
  text: string;
  className?: string;
};

const cn = (...xs: Array<string | undefined | false>) => xs.filter(Boolean).join(" ");

/**
 * TextWindow – großes Textfenster mit 16:9 Verhältnis.
 * Nutzt Tailwind `aspect-video` für 16:9 und passt die Breite an den Container an.
 */
export default function TextWindow({ text, className }: TextWindowProps) {
  return (
    <div
      className={cn(
        "aspect-video w-full rounded-2xl border shadow-md",
        "bg-white dark:bg-neutral-900 border-gray-200 dark:border-neutral-800",
        "p-6 flex items-center justify-center text-center",
        className
      )}
    >
      <p className="text-lg md:text-xl leading-relaxed text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
        {text}
      </p>
    </div>
  );
}

/**
 * Beispiel:
 * <TextWindow text="Hier steht ein längerer Absatz, der in einem großen Fenster angezeigt wird." />
 */