"use client";

import { useMemo } from "react";
import type { TimeseriesPoint } from "../lib/types";

type Props = {
  points: TimeseriesPoint[];
  currentTime: number;
  jointUnits?: string;
};

const JOINT_COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f87171", "#60a5fa"];
const GRIPPER_COLOR = "#e5e7eb";

export function TimeseriesChart({ points, currentTime, jointUnits = "units" }: Props) {
  const { width, height, padX, padY, paths, gripperPath, tMin, tMax } = useMemo(() => {
    const w = 520;
    const h = 220;
    const px = 32;
    const py = 18;
    if (points.length === 0) {
      return { width: w, height: h, padX: px, padY: py, paths: [], gripperPath: "", tMin: 0, tMax: 1 };
    }
    const tMin = points[0].t;
    const tMax = points[points.length - 1].t || tMin + 1;

    const allJointValues = points.flatMap((p) => p.joints);
    const lo = Math.min(...allJointValues, -1);
    const hi = Math.max(...allJointValues, 1);

    const xFor = (t: number) => px + ((t - tMin) / (tMax - tMin)) * (w - 2 * px);
    const yFor = (v: number) => h - py - ((v - lo) / (hi - lo)) * (h - 2 * py);

    const paths = JOINT_COLORS.map((color, jointIdx) => {
      const d = points
        .map((p, i) => {
          const v = p.joints[jointIdx] ?? 0;
          return `${i === 0 ? "M" : "L"} ${xFor(p.t).toFixed(2)} ${yFor(v).toFixed(2)}`;
        })
        .join(" ");
      return { color, d };
    });

    const gripperPath = points
      .map((p, i) => {
        const v = p.gripper;
        // gripper rides at the bottom band
        const y = h - py - v * (h - 2 * py) * 0.3;
        return `${i === 0 ? "M" : "L"} ${xFor(p.t).toFixed(2)} ${y.toFixed(2)}`;
      })
      .join(" ");

    return { width: w, height: h, padX: px, padY: py, paths, gripperPath, tMin, tMax };
  }, [points]);

  const cursorX = useMemo(() => {
    if (points.length === 0) return null;
    if (tMax === tMin) return padX;
    const clamped = Math.min(Math.max(currentTime, tMin), tMax);
    return padX + ((clamped - tMin) / (tMax - tMin)) * (width - 2 * padX);
  }, [currentTime, points.length, tMin, tMax, padX, width]);

  return (
    <div className="rounded-xl bg-panel border border-slate-800 p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs uppercase tracking-widest text-slate-400">Joint timeseries</h4>
        <span className="text-xs font-mono text-slate-500">t = {currentTime.toFixed(2)}s</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
        <rect x={0} y={0} width={width} height={height} fill="#0b1220" />
        <g stroke="#1f2937" strokeWidth={1}>
          {[0.25, 0.5, 0.75].map((f) => (
            <line
              key={f}
              x1={padX}
              x2={width - padX}
              y1={padY + f * (height - 2 * padY)}
              y2={padY + f * (height - 2 * padY)}
            />
          ))}
        </g>
        {paths.map((p, i) => (
          <path key={i} d={p.d} stroke={p.color} strokeWidth={1.5} fill="none" />
        ))}
        <path d={gripperPath} stroke={GRIPPER_COLOR} strokeWidth={1.5} fill="none" strokeDasharray="3 3" />
        {cursorX !== null && (
          <line x1={cursorX} x2={cursorX} y1={padY} y2={height - padY} stroke="#22d3ee" strokeWidth={1} />
        )}
        <text x={padX} y={padY - 4} fontSize={10} fill="#64748b" fontFamily="ui-monospace, monospace">
          joints ({jointUnits})
        </text>
      </svg>
      <div className="mt-2 flex flex-wrap gap-2 text-[10px] font-mono">
        {JOINT_COLORS.map((c, i) => (
          <span key={i} className="flex items-center gap-1 text-slate-400">
            <span style={{ backgroundColor: c }} className="inline-block w-2.5 h-2.5 rounded-sm" />
            j{i}
          </span>
        ))}
        <span className="flex items-center gap-1 text-slate-400">
          <span style={{ backgroundColor: GRIPPER_COLOR }} className="inline-block w-2.5 h-2.5 rounded-sm" />
          gripper
        </span>
      </div>
    </div>
  );
}
