import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VLA-DataEngine",
  description:
    "Hong Kong robotics data engine for turning SO-101 demos into factory-ready VLA datasets",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink text-slate-100 antialiased font-sans flex flex-col">
        {children}
      </body>
    </html>
  );
}
