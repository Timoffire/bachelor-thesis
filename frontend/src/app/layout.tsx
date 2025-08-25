import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Metric Dashboard",
  description: "Simple Next.js Metric Viewer",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body className="min-h-screen bg-gray-50 dark:bg-neutral-950 text-gray-900 dark:text-gray-100">
        <main className="max-w-5xl mx-auto p-6">{children}</main>
      </body>
    </html>
  );
}