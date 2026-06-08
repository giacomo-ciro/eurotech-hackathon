const STEPS = [
  {
    n: "01",
    title: "Capture the skill",
    body:
      "Start with a concrete physical task: grasp household objects, sort parts, stage parcels, or handle lab equipment. We record the robot demonstrations and raw trajectories.",
  },
  {
    n: "02",
    title: "Generate training signal",
    body:
      "The platform adds semantic labels, task descriptions, trajectory metadata, and replayable evidence so the data explains what the robot did and why it matters.",
  },
  {
    n: "03",
    title: "Package for model teams",
    body:
      "Ship model-ready datasets for LeRobot and Rerun inspection, ready for edge VLA adaptation, evaluation, and reuse across related robot workflows.",
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
            A practical pipeline for turning local physical tasks into reusable
            robot training data.
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
