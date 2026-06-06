"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "Collection" },
  { href: "/datasets", label: "Datasets" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="flex items-center justify-between border-b border-slate-800 px-6 py-3">
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-3">
          <span className="text-xl font-bold tracking-tight">VLA-DataEngine</span>
          <span className="hidden md:inline text-xs uppercase tracking-widest text-slate-500">
            Synthetic data marketplace
          </span>
        </Link>
        <nav className="flex items-center gap-1">
          {TABS.map((tab) => {
            const active = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`px-3 py-1.5 rounded-md text-sm transition ${
                  active
                    ? "bg-accent/15 text-accent"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="text-xs font-mono text-slate-500">alex@vla.dev</div>
    </header>
  );
}
