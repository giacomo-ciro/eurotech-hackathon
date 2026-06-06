import Link from "next/link";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 h-[480px] w-[820px] rounded-full bg-accent/10 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-40 right-0 h-[260px] w-[260px] rounded-full bg-ok/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-4xl px-6 pt-24 pb-20 text-center">
        <p className="text-xs uppercase tracking-[0.3em] text-accent font-mono mb-6">
          Bootstrap physical AI in hours, not months
        </p>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight leading-tight">
          Synthetic data that ships{" "}
          <span className="text-accent">physical AI</span> in hours, not months.
        </h1>
        <p className="mt-6 text-lg text-slate-300 leading-relaxed max-w-2xl mx-auto">
          VLA-DataEngine bootstraps a handful of raw robot trajectories into
          deployment-ready LeRobot datasets — semantically rich, edge-tuned, and
          ready for SmolVLA fine-tuning.
        </p>
        <div className="mt-10 flex items-center justify-center gap-3">
          <Link
            href="/platform"
            className="inline-flex items-center gap-2 rounded-full bg-accent text-ink font-semibold px-6 py-3 text-base hover:bg-accent/90 transition shadow-xl shadow-accent/30"
          >
            Open the platform
            <span aria-hidden>→</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
