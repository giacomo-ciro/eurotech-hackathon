import Link from "next/link";

export function MarketingHeader() {
  return (
    <header className="sticky top-0 z-30 backdrop-blur-md bg-ink/70 border-b border-slate-800">
      <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-3">
          <span className="text-lg font-bold tracking-tight">VLA-DataEngine</span>
          <span className="hidden md:inline text-xs uppercase tracking-widest text-slate-500">
            Hong Kong to factory floor
          </span>
        </Link>
        <Link
          href="/platform"
          className="rounded-full bg-accent text-ink font-semibold text-sm px-4 py-2 hover:bg-accent/90 transition shadow-lg shadow-accent/20"
        >
          Platform →
        </Link>
      </div>
    </header>
  );
}
