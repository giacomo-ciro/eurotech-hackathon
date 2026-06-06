import type { Patient } from "../lib/types";

type Props = { patient: Patient };

export function PatientCard({ patient }: Props) {
  return (
    <article className="rounded-xl bg-panel border border-slate-800 p-4">
      <header className="flex items-center justify-between mb-3">
        <h3 className="text-xs uppercase tracking-widest text-slate-400">Patient</h3>
        <span className="text-xs font-mono text-slate-500">{patient.id}</span>
      </header>
      <div className="flex items-baseline gap-3">
        <p className="text-lg font-semibold">{patient.name}</p>
        {patient.name_zh && <p className="text-base text-slate-300">{patient.name_zh}</p>}
      </div>
      <p className="text-sm text-slate-400 mt-1">
        {patient.age} y/o · {patient.sex} · {patient.languages.join(" / ")}
      </p>
      <div className="mt-3 text-sm">
        <p className="text-slate-400">
          Allergies:{" "}
          {patient.allergies.length > 0 ? (
            <span className="text-warn font-medium">{patient.allergies.join(", ")}</span>
          ) : (
            <span className="text-slate-500">none on file</span>
          )}
        </p>
        {patient.notes && (
          <p className="mt-2 text-slate-400 leading-snug">{patient.notes}</p>
        )}
      </div>
    </article>
  );
}
