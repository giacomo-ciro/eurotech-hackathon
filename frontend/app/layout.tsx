import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dispensr",
  description: "AI pharmacy dispensing workcell",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink text-slate-100 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
