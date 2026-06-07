const USE_CASES = [
  {
    title: "Household grasping",
    body:
      "Train robots on cups, utensils, bottles, toys, laundry, and other everyday objects that generic datasets miss.",
  },
  {
    title: "Manufacturing QA",
    body:
      "Generate inspection, sorting, staging, and defect-handling datasets from local production workflows.",
  },
  {
    title: "Logistics and warehousing",
    body:
      "Capture parcel handling, bin picking, SKU staging, and pick-and-place demonstrations for warehouse automation.",
  },
  {
    title: "Lab and service tasks",
    body:
      "Package careful handling workflows for trays, tubes, tools, counters, shelves, and other structured environments.",
  },
];

export function UseCases() {
  return (
    <section className="relative">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="mb-10 max-w-3xl">
          <p className="font-mono text-xs font-bold uppercase tracking-[0.22em] text-accent">
            Use cases
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight md:text-5xl">
            One data foundry, many robot skills.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-slate-400 md:text-lg">
            The company is horizontal: every new robot skill needs local
            demonstrations, labels, replay, and validation before it becomes a
            reusable training asset.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {USE_CASES.map((useCase) => (
            <article
              key={useCase.title}
              className="rounded-lg border border-slate-800 bg-panel/70 p-6 transition hover:border-accent/40"
            >
              <h3 className="text-xl font-semibold tracking-tight">
                {useCase.title}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">
                {useCase.body}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
