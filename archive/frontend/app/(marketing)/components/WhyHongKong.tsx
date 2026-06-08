const REASONS = [
  {
    title: "Close to real physical workflows",
    body:
      "The region around Hong Kong creates endless robot tasks: grasping, sorting, packing, inspection, logistics, lab handling, and service automation.",
  },
  {
    title: "Strong AI sector",
    body:
      "Hong Kong has the AI talent and research base to turn those real-world tasks into usable datasets, model-adaptation pipelines, and deployable robotics systems.",
  },
  {
    title: "Bridge from task to dataset",
    body:
      "VLA-DataEngine sits between local operators with physical tasks and AI teams that need clean, validated robot data.",
  },
];

export function WhyHongKong() {
  return (
    <section className="relative border-y border-slate-800 bg-panel/40">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-10 px-6 py-16 md:grid-cols-[0.85fr_1.15fr] md:py-20">
        <div>
          <p className="font-mono text-xs font-bold uppercase tracking-[0.22em] text-warn">
            Hong Kong advantage
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight md:text-5xl">
            Why Hong Kong
          </h2>
          <p className="mt-5 text-base leading-relaxed text-slate-300 md:text-lg">
            Hong Kong is uniquely positioned for physical-AI data generation:
            it sits next to a massive manufacturing ecosystem while also having
            a strong AI sector of its own. That makes it a practical bridge
            between real physical workflows and the AI systems that need local
            training data.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {REASONS.map((reason) => (
            <article
              key={reason.title}
              className="rounded-lg border border-slate-800 bg-ink/70 p-6"
            >
              <h3 className="text-xl font-semibold tracking-tight">
                {reason.title}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">
                {reason.body}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
