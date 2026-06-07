const STEPS = [
  {
    n: "01",
    title: "Record in Hong Kong",
    body:
      "Capture a handful of teleoperation demos on the SO-101. Just the trajectories from the workflow you need to bring into production.",
  },
  {
    n: "02",
    title: "Augment with domain language",
    body:
      "Claude reads the camera frames and generates dense technical captions plus semantic variations for manufacturing, lab, logistics, or QA tasks.",
  },
  {
    n: "03",
    title: "Deploy near the factory floor",
    body:
      "Fine-tune SmolVLA locally, validate on the arm, and carry the adapted policy into the Hong Kong-Shenzhen hardware iteration loop.",
  },
];

export function HowItWorks() {
  return (
    <section className="relative">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="mb-10 text-center">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            How it works
          </h2>
          <p className="mt-3 text-slate-400 max-w-2xl mx-auto">
            A two-model pipeline for turning local robot demos into training
            data that can travel from a Hong Kong lab to Asian manufacturing
            partners.
          </p>
        </div>
        <ol className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {STEPS.map((step) => (
            <li
              key={step.n}
              className="rounded-2xl bg-panel border border-slate-800 p-6 hover:border-accent/40 transition"
            >
              <div className="text-xs font-mono tracking-widest text-accent mb-3">
                {step.n}
              </div>
              <h3 className="text-xl font-semibold tracking-tight">{step.title}</h3>
              <p className="mt-3 text-sm text-slate-400 leading-relaxed">
                {step.body}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
