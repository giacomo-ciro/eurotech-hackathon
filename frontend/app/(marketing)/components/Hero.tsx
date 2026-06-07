import Link from "next/link";

const PROOF_POINTS = [
  "Hong Kong base",
  "Shenzhen supply chain",
  "Local VLA fine-tuning",
];

export function Hero() {
  return (
    <section className="relative min-h-[calc(100vh-57px)] overflow-hidden">
      <div
        aria-hidden
        className="absolute inset-0 bg-[url('/hk-robot-hero.png')] bg-cover bg-center"
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-[linear-gradient(90deg,rgba(11,18,32,0.98)_0%,rgba(11,18,32,0.88)_40%,rgba(11,18,32,0.58)_72%,rgba(11,18,32,0.88)_100%)]"
      />
      <div
        aria-hidden
        className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-ink to-transparent"
      />

      <div className="relative mx-auto grid min-h-[calc(100vh-57px)] max-w-6xl grid-cols-1 items-center px-6 py-20 md:grid-cols-[1.05fr_0.95fr] md:py-28">
        <div className="max-w-3xl">
          <p className="font-mono text-xs font-bold uppercase tracking-[0.24em] text-accent">
            Built in Hong Kong for the robotics supply chain next door
          </p>
          <h1 className="mt-5 text-4xl font-bold leading-[0.98] tracking-tight md:text-6xl lg:text-7xl">
            Turn Hong Kong robot demos into{" "}
            <span className="text-accent">factory-ready physical AI.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-200 md:text-xl">
            VLA-DataEngine uses Claude to transform a handful of SO-101
            demonstrations into rich LeRobot datasets, then fine-tunes compact
            VLA models for local deployment. Hong Kong gives teams a launchpad:
            global capital, technical talent, and direct proximity to Shenzhen's
            manufacturing ecosystem.
          </p>
          <div className="mt-7 flex flex-wrap gap-2">
            {PROOF_POINTS.map((point) => (
              <span
                key={point}
                className="rounded-full border border-accent/35 bg-sky-950/50 px-3 py-2 font-mono text-xs font-bold uppercase tracking-[0.08em] text-sky-100"
              >
                {point}
              </span>
            ))}
          </div>
          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href="/platform"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-accent px-6 py-3 text-base font-semibold text-ink shadow-xl shadow-accent/30 transition hover:bg-accent/90"
            >
              Open the platform
              <span aria-hidden>→</span>
            </Link>
            <p className="text-sm text-slate-300">
              From lab bench to production floor, without waiting months for
              labeled robotics data.
            </p>
          </div>
        </div>

        <div aria-hidden className="hidden md:block" />
      </div>
    </section>
  );
}
