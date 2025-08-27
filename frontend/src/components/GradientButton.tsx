"use client";

import * as React from "react";
import Link from "next/link";

export type GradientButtonProps = {
  children: React.ReactNode;
  href?: string; // optional: rendert als <Link>
  onClick?: () => void; // optional: Button-Handler
  className?: string;
  size?: "sm" | "md" | "lg";
  ariaLabel?: string;
  rounded?: "lg" | "xl" | "2xl" | "3xl"; // für Konsistenz mit MetricCard
  wide?: boolean; // falls true: Button wird etwas breiter als Text
};

const cn = (...xs: Array<string | undefined | false>) => xs.filter(Boolean).join(" ");

export default function GradientButton({
  children,
  href,
  onClick,
  className,
  size = "md",
  ariaLabel,
  rounded = "3xl",
  wide = true,
}: GradientButtonProps) {
  const sizes = {
    sm: "text-sm px-6 py-2",
    md: "text-base px-8 py-3",
    lg: "text-lg px-10 py-3.5",
  } as const;

  const radius = {
    lg: "rounded-lg",
    xl: "rounded-xl",
    "2xl": "rounded-2xl",
    "3xl": "rounded-3xl",
  } as const;

  const base = cn(
    "inline-flex items-center justify-center select-none",
    sizes[size],
    radius[rounded],
    "bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500",
    "text-white font-medium shadow-lg",
    "transition-all duration-300 ease-out",
    "hover:shadow-2xl hover:-translate-y-0.5 active:translate-y-0",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pink-400/70",
    "relative overflow-hidden",
    "cursor-pointer",
    wide && "min-w-[8rem]", // sorgt für zusätzliche Breite
    className
  );

  const content = <span className="relative z-10 leading-none">{children}</span>;
  const glow = (
    <span className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-white/5" />
  );

  if (href) {
    return (
      <Link href={href} aria-label={ariaLabel} className={cn(base, "group")}>
        {content}
        {glow}
      </Link>
    );
  }

  return (
    <button type="button" aria-label={ariaLabel} onClick={onClick} className={cn(base, "group")}>
      {content}
      {glow}
    </button>
  );
}

/**
 * Beispiel:
 * <GradientButton onClick={() => console.log('Clicked!')}>Back</GradientButton>
 * <GradientButton href="/" size="lg">Zur Übersicht</GradientButton>
 */
