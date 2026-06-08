"use client";

import { useMemo } from "react";
import type { Caption } from "../lib/types";

type Props = {
  captions: Caption[];
  currentTime: number;
};

export function CaptionTrack({ captions, currentTime }: Props) {
  const activeIndex = useMemo(() => {
    return captions.findIndex(
      (c) => currentTime >= c.t_start && currentTime <= c.t_end,
    );
  }, [captions, currentTime]);

  return (
    <div className="rounded-xl bg-panel border border-slate-800 p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs uppercase tracking-widest text-slate-400">Frame captions</h4>
        <span className="text-xs font-mono text-slate-500">{captions.length} segments</span>
      </div>
      <ul className="space-y-2 max-h-72 overflow-y-auto pr-1">
        {captions.map((c, i) => {
          const active = i === activeIndex;
          return (
            <li
              key={i}
              className={`text-sm rounded-md border p-2 transition ${
                active
                  ? "border-accent bg-accent/10 text-slate-100"
                  : "border-slate-800 bg-slate-900/40 text-slate-400"
              }`}
            >
              <div className="flex items-center justify-between text-[10px] font-mono mb-1">
                <span>
                  {c.t_start.toFixed(1)}s → {c.t_end.toFixed(1)}s
                </span>
                <span>confidence {c.confidence.toFixed(2)}</span>
              </div>
              <p className="leading-snug">{c.text}</p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
