const REASONS = [
  {
    title: "Gateway to Shenzhen",
    body:
      "Prototype in Hong Kong, iterate with nearby manufacturing partners, and keep the model-training loop close to the hardware.",
  },
  {
    title: "Made for specialized workflows",
    body:
      "Manufacturing QA, lab handling, warehouse sorting, and robotics OEM demos all depend on vocabulary that generic VLAs do not understand out of the box.",
  },
  {
    title: "Local edge deployment",
    body:
      "Generate semantic training data with Claude, fine-tune SmolVLA locally, and run the adapted policy on affordable robot hardware.",
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
            Robotics companies do not only need models. They need hardware
            iteration, supplier access, manufacturing partners, and a credible
            market entry point. Hong Kong sits at that intersection: close
            enough to Shenzhen for rapid hardware iteration, connected enough
            for international commercialization, and dense enough for robotics,
            logistics, lab automation, and advanced manufacturing pilots.
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
