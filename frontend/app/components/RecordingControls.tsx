"use client";

import { useMemo } from "react";
import { RERUN_URL } from "../lib/api";
import type { RobotStateEvent, Session } from "../lib/types";

const STAGES = [
  { key: "arming", label: "Arm" },
  { key: "recording", label: "Record" },
  { key: "captioning", label: "Caption" },
  { key: "saved", label: "Save" },
] as const;

const STAGE_INDEX: Record<string, number> = STAGES.reduce((acc, s, i) => {
  acc[s.key] = i;
  return acc;
}, {} as Record<string, number>);

function stageColor(state: RobotStateEvent): string {
  if (state.stage === "error") return "bg-bad";
  if (state.stage === "offline") return "bg-slate-500";
  if (state.stage === "saved") return "bg-ok";
  return "bg-accent";
}

type Props = {
  state: RobotStateEvent;
  session: Session | null;
  onStart: () => void;
  onStop: () => void;
  isWorking: boolean;
};

export function RecordingControls({ state, session, onStart, onStop, isWorking }: Props) {
  const activeIndex = useMemo(() => {
    if (state.stage in STAGE_INDEX) return STAGE_INDEX[state.stage];
    return -1;
  }, [state.stage]);

  const canStart = !!session && state.stage !== "offline" && state.stage !== "recording";
  const canStop = state.stage === "recording" || state.stage === "captioning";

  return (
    <section className="flex flex-col gap-4 h-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${stageColor(state)}`} />
          <h2 className="text-lg font-semibold tracking-tight">Robot live stream</h2>
        </div>
        <div className="text-sm text-slate-400 font-mono">
          {state.stage}
          {state.detail ? ` · ${state.detail}` : ""}
        </div>
      </div>

      <div className="relative flex-1 rounded-2xl overflow-hidden bg-black border border-slate-800 shadow-2xl">
        <iframe
          src={RERUN_URL}
          title="LeRobot rerun viewer"
          className="absolute inset-0 h-full w-full"
          allow="autoplay; fullscreen"
        />
        {state.stage === "offline" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/70 text-center px-6">
            <div>
              <p className="text-slate-300 text-base mb-2">Robot bridge not connected.</p>
              <p className="text-slate-500 text-sm font-mono">
                Start with: <span className="text-accent">uv run python -m robot_bridge.app.main</span>
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="rounded-xl bg-panel border border-slate-800 p-4">
        <div className="grid grid-cols-4 gap-2 mb-4">
          {STAGES.map((stage, idx) => {
            const done = activeIndex > idx;
            const active = activeIndex === idx;
            return (
              <div
                key={stage.key}
                className={`flex flex-col items-center text-xs uppercase tracking-wider py-2 rounded-md border ${
                  done
                    ? "border-ok/40 bg-ok/10 text-ok"
                    : active
                    ? "border-accent/60 bg-accent/10 text-accent"
                    : "border-slate-800 bg-slate-900/40 text-slate-500"
                }`}
              >
                <span className="font-mono text-[10px]">{idx + 1}</span>
                <span>{stage.label}</span>
              </div>
            );
          })}
        </div>
        <div className="flex gap-3">
          <button
            onClick={onStart}
            disabled={!canStart || isWorking}
            className="flex-1 rounded-lg bg-accent text-ink font-semibold py-3 hover:bg-accent/90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isWorking && state.stage === "recording" ? "Recording…" : "Start recording"}
          </button>
          <button
            onClick={onStop}
            disabled={!canStop}
            className="rounded-lg border border-slate-700 text-slate-200 px-4 hover:border-slate-500 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Stop & save
          </button>
        </div>
      </div>
    </section>
  );
}
