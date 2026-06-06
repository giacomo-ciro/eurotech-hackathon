import type { ActivePrescription, Medicine, Prescription } from "../lib/types";

type Props = {
  medicine: Medicine;
  prescription: Prescription;
  active: ActivePrescription;
};

function trayLabel(tray: string): string {
  return tray.charAt(0).toUpperCase() + tray.slice(1);
}

export function MedicineCard({ medicine, prescription, active }: Props) {
  const confidence = Math.round(active.vision_confidence * 100);
  return (
    <article className="rounded-xl bg-panel border border-slate-800 p-4">
      <header className="flex items-center justify-between mb-3">
        <h3 className="text-xs uppercase tracking-widest text-slate-400">Prescription</h3>
        <span className="text-xs font-mono text-slate-500">{prescription.id}</span>
      </header>

      <div className="space-y-1">
        <p className="text-lg font-semibold leading-tight">
          {medicine.drug_name}{" "}
          <span className="text-slate-400 font-normal">· {medicine.strength}</span>
        </p>
        <p className="text-sm text-slate-400">
          {medicine.generic_name} · {medicine.drug_class}
        </p>
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-y-2 gap-x-3 text-sm">
        <div>
          <dt className="text-slate-500">Form</dt>
          <dd>{medicine.dosage_form}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Route</dt>
          <dd>{medicine.route_of_administration}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Tray</dt>
          <dd className="font-semibold text-accent">{trayLabel(prescription.tray)}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Schedule</dt>
          <dd>{prescription.quantity} × {trayLabel(prescription.tray)}</dd>
        </div>
      </dl>

      {prescription.instructions && (
        <p className="mt-3 text-sm text-slate-300 italic">"{prescription.instructions}"</p>
      )}

      <div className="mt-4 flex items-center justify-between rounded-md bg-slate-900/60 border border-slate-800 px-3 py-2 text-xs">
        <div className="flex items-center gap-2">
          <span className={active.match ? "text-ok" : "text-warn"}>
            {active.match ? "✓ Match" : "⚠ Pending"}
          </span>
          <span className="text-slate-500">Confidence {confidence}%</span>
        </div>
        <span className="font-mono text-slate-500">NDC {medicine.ndc}</span>
      </div>

      <details className="mt-3 text-sm text-slate-400">
        <summary className="cursor-pointer text-slate-300">Side effects & warnings</summary>
        <p className="mt-2"><span className="text-slate-500">Side effects:</span> {medicine.side_effects}</p>
        <p className="mt-1"><span className="text-slate-500">Warnings:</span> {medicine.warnings_and_precautions}</p>
        <p className="mt-1"><span className="text-slate-500">Contraindications:</span> {medicine.contraindications}</p>
      </details>
    </article>
  );
}
