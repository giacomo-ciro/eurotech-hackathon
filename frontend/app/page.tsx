"use client";

import { useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { MedicineCard } from "./components/MedicineCard";
import { PatientCard } from "./components/PatientCard";
import { VideoPane } from "./components/VideoPane";
import { useActivePrescription } from "./hooks/useActivePrescription";
import { useRobotState } from "./hooks/useRobotState";
import { startDispense } from "./lib/api";

export default function Page() {
  const { data, error } = useActivePrescription();
  const robot = useRobotState();
  const [dispensing, setDispensing] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleDispense() {
    if (!data) return;
    setDispensing(true);
    setActionError(null);
    try {
      await startDispense(data.prescription.id);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : String(err));
    } finally {
      // The robot WS will animate the rest; release the button shortly.
      window.setTimeout(() => setDispensing(false), 1500);
    }
  }

  return (
    <main className="h-screen flex flex-col">
      <header className="flex items-center justify-between border-b border-slate-800 px-6 py-3">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold tracking-tight">Dispensr</span>
          <span className="text-xs uppercase tracking-widest text-slate-500">
            AI pharmacy workcell · HK-01
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
          <span className="flex items-center gap-2">
            <span
              className={`inline-block h-2 w-2 rounded-full ${
                robot.stage === "offline" ? "bg-slate-500" : "bg-ok"
              }`}
            />
            robot: {robot.stage}
          </span>
          <span>alex@clinic</span>
        </div>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[minmax(0,1.4fr)_minmax(360px,1fr)] gap-4 p-6 overflow-hidden">
        <div className="min-h-0 flex flex-col">
          <VideoPane state={robot} onDispense={handleDispense} isDispensing={dispensing} />
          {actionError && (
            <p className="mt-2 text-sm text-bad">⚠ {actionError}</p>
          )}
        </div>

        <aside className="min-h-0 flex flex-col gap-4 overflow-y-auto pr-1">
          {error && (
            <div className="rounded-md bg-bad/10 border border-bad/40 text-bad text-sm p-3">
              Backend unreachable: {error}
            </div>
          )}
          {!data && !error && (
            <div className="rounded-md bg-panel border border-slate-800 text-slate-400 text-sm p-3">
              Loading active prescription…
            </div>
          )}
          {data && (
            <>
              <PatientCard patient={data.patient} />
              <MedicineCard
                medicine={data.medicine}
                prescription={data.prescription}
                active={data.active}
              />
              <div className="flex-1 min-h-[320px]">
                <ChatPanel medicine={data.medicine} />
              </div>
            </>
          )}
        </aside>
      </div>
    </main>
  );
}
