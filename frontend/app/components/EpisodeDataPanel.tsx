"use client";

import { useMemo } from "react";
import type { LeRobotEpisodeData } from "../lib/types";

type Props = {
  data: LeRobotEpisodeData | null;
  episodeTime: number; // seconds since episode start (0..duration)
};

function shortName(name: string): string {
  return name.replace(/\.pos$/, "").replace(/_/g, " ");
}

export function EpisodeDataPanel({ data, episodeTime }: Props) {
  const frameIndex = useMemo(() => {
    if (!data) return 0;
    const fi = Math.floor(episodeTime * data.fps);
    return Math.max(0, Math.min(fi, data.length_frames - 1));
  }, [data, episodeTime]);

  const { actionRow, stateRow, ranges } = useMemo(() => {
    if (!data) {
      return { actionRow: [] as number[], stateRow: [] as number[], ranges: [] as Array<[number, number]> };
    }
    const a = data.action[frameIndex] ?? [];
    const s = data.state[frameIndex] ?? [];
    const r: Array<[number, number]> = data.joint_names.map((_, j) => {
      let lo = Infinity, hi = -Infinity;
      for (let i = 0; i < data.action.length; i++) {
        const av = data.action[i][j];
        const sv = data.state[i][j];
        if (av < lo) lo = av;
        if (av > hi) hi = av;
        if (sv < lo) lo = sv;
        if (sv > hi) hi = sv;
      }
      if (!isFinite(lo) || !isFinite(hi) || lo === hi) {
        lo = -1;
        hi = 1;
      }
      return [lo, hi];
    });
    return { actionRow: a, stateRow: s, ranges: r };
  }, [data, frameIndex]);

  const CHART_W = 120;
  const CHART_H = 28;

  const paths = useMemo(() => {
    if (!data) return [] as Array<{ action: string; state: string }>;
    const N = data.length_frames;
    if (N < 2) return data.joint_names.map(() => ({ action: "", state: "" }));
    return data.joint_names.map((_, j) => {
      const [lo, hi] = ranges[j];
      const span = hi - lo || 1;
      const action: string[] = [];
      const state: string[] = [];
      for (let i = 0; i < N; i++) {
        const x = ((i / (N - 1)) * CHART_W).toFixed(1);
        const yA = (CHART_H - ((data.action[i][j] - lo) / span) * CHART_H).toFixed(1);
        const yS = (CHART_H - ((data.state[i][j] - lo) / span) * CHART_H).toFixed(1);
        action.push(`${i === 0 ? "M" : "L"} ${x} ${yA}`);
        state.push(`${i === 0 ? "M" : "L"} ${x} ${yS}`);
      }
      return { action: action.join(" "), state: state.join(" ") };
    });
  }, [data, ranges]);

  const cursorX = useMemo(() => {
    if (!data || data.length_frames < 2) return 0;
    return (frameIndex / (data.length_frames - 1)) * CHART_W;
  }, [data, frameIndex]);

  if (!data) {
    return (
      <article className="rounded-xl bg-panel border border-slate-800 p-4">
        <h3 className="text-xs uppercase tracking-widest text-slate-400">Frame data</h3>
        <p className="text-sm text-slate-500 mt-3 italic">
          Loading episode arrays…
        </p>
      </article>
    );
  }

  return (
    <article className="rounded-xl bg-panel border border-slate-800 p-4">
      <header className="flex items-center justify-between mb-3">
        <h3 className="text-xs uppercase tracking-widest text-slate-400">Frame data</h3>
        <span className="text-xs font-mono text-slate-500">
          ep #{data.episode_index.toString().padStart(2, "0")} · {data.task} · f={frameIndex}/{data.length_frames - 1}
        </span>
      </header>

      <div className="space-y-3">
        {data.joint_names.map((name, j) => {
          const a = actionRow[j] ?? 0;
          const s = stateRow[j] ?? 0;
          const p = paths[j] ?? { action: "", state: "" };

          return (
            <div key={name}>
              <div className="flex items-center justify-between text-[10px] uppercase tracking-wider font-mono text-slate-500 mb-1">
                <span>{shortName(name)}</span>
                <span>
                  <span className="text-accent">a={a.toFixed(2)}</span>{" · "}
                  <span className="text-ok">s={s.toFixed(2)}</span>
                </span>
              </div>
              <svg
                viewBox={`0 0 ${CHART_W} ${CHART_H}`}
                preserveAspectRatio="none"
                className="block w-full h-7 rounded-sm bg-slate-900 border border-slate-800"
              >
                <path
                  d={p.state}
                  stroke="#34d399"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  fill="none"
                  vectorEffect="non-scaling-stroke"
                />
                <path
                  d={p.action}
                  stroke="#22d3ee"
                  strokeWidth={1.5}
                  fill="none"
                  vectorEffect="non-scaling-stroke"
                />
                <line
                  x1={cursorX}
                  x2={cursorX}
                  y1={0}
                  y2={CHART_H}
                  stroke="#94a3b8"
                  strokeWidth={1}
                  vectorEffect="non-scaling-stroke"
                />
              </svg>
            </div>
          );
        })}
      </div>

      <p className="mt-3 text-[10px] text-slate-500 font-mono">
        solid line = action · dashed line = observation.state · vertical = current frame
      </p>
    </article>
  );
}
