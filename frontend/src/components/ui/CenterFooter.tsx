"use client";
import React from "react";

export default function CenterFooter({ children }: { children: React.ReactNode }) {
  return (
    <div className="fixed inset-x-0 bottom-6 flex justify-center pointer-events-none">
      <div className="pointer-events-auto">{children}</div>
    </div>
  );
}
