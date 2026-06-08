"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { TimeseriesPoint } from "../lib/types";

type Props = {
  points: TimeseriesPoint[];
  currentTime: number;
  onTimeChange: (time: number) => void;
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function nearestFrameIndex(points: TimeseriesPoint[], time: number): number {
  if (points.length <= 1) return 0;
  if (time <= points[0].t) return 0;
  const lastIndex = points.length - 1;
  if (time >= points[lastIndex].t) return lastIndex;

  let lo = 0;
  let hi = lastIndex;
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    if (points[mid].t <= time) lo = mid;
    else hi = mid;
  }

  return time - points[lo].t <= points[hi].t - time ? lo : hi;
}

export function TrajectoryPlaybackControls({ points, currentTime, onTimeChange }: Props) {
  const [playing, setPlaying] = useState(false);
  const rafRef = useRef<number | null>(null);
  const tickRef = useRef<number | null>(null);
  const timeRef = useRef(currentTime);

  const startTime = points[0]?.t ?? 0;
  const endTime = points[points.length - 1]?.t ?? 0;
  const maxFrame = Math.max(points.length - 1, 0);
  const currentFrame = useMemo(() => nearestFrameIndex(points, currentTime), [points, currentTime]);
  const duration = Math.max(endTime - startTime, 0);
  const elapsedTime = clamp(currentTime - startTime, 0, duration);
  const disabled = points.length === 0;

  useEffect(() => {
    timeRef.current = currentTime;
  }, [currentTime]);

  useEffect(() => {
    setPlaying(false);
    tickRef.current = null;
    return () => {
      if (rafRef.current !== null) window.cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    };
  }, [points]);

  useEffect(() => {
    if (!playing || disabled) return;

    const tick = (now: number) => {
      if (tickRef.current === null) tickRef.current = now;
      const deltaSeconds = (now - tickRef.current) / 1000;
      tickRef.current = now;

      const nextTime = clamp(timeRef.current + deltaSeconds, startTime, endTime);
      timeRef.current = nextTime;
      onTimeChange(nextTime);

      if (nextTime >= endTime) {
        setPlaying(false);
        tickRef.current = null;
        rafRef.current = null;
        return;
      }
      rafRef.current = window.requestAnimationFrame(tick);
    };

    rafRef.current = window.requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) window.cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
      tickRef.current = null;
    };
  }, [disabled, endTime, onTimeChange, playing, startTime]);

  const selectFrame = (frame: number) => {
    const index = clamp(frame, 0, maxFrame);
    setPlaying(false);
    tickRef.current = null;
    onTimeChange(points[index]?.t ?? 0);
  };

  const togglePlayback = () => {
    if (disabled) return;
    if (playing) {
      setPlaying(false);
      return;
    }
    if (currentTime >= endTime) {
      onTimeChange(startTime);
      timeRef.current = startTime;
    }
    tickRef.current = null;
    setPlaying(true);
  };

  return (
    <section className="rounded-lg border border-slate-800 bg-panel p-4">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={togglePlayback}
          disabled={disabled}
          className="h-10 min-w-24 rounded-md bg-accent px-4 text-sm font-semibold text-ink transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {playing ? "Pause" : "Play"}
        </button>
        <button
          type="button"
          onClick={() => selectFrame(currentFrame - 1)}
          disabled={disabled || currentFrame <= 0}
          className="h-10 rounded-md border border-slate-700 px-3 text-sm text-slate-200 transition hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Prev
        </button>
        <button
          type="button"
          onClick={() => selectFrame(currentFrame + 1)}
          disabled={disabled || currentFrame >= maxFrame}
          className="h-10 rounded-md border border-slate-700 px-3 text-sm text-slate-200 transition hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Next
        </button>
        <label className="flex items-center gap-2 text-xs text-slate-400">
          Frame
          <input
            type="number"
            min={1}
            max={Math.max(points.length, 1)}
            value={currentFrame + 1}
            onChange={(event) => selectFrame(Number(event.target.value) - 1)}
            disabled={disabled}
            className="h-10 w-24 rounded-md border border-slate-700 bg-slate-950 px-2 font-mono text-sm text-slate-100 focus:border-accent focus:outline-none disabled:opacity-50"
          />
          <span className="font-mono text-slate-500">/ {points.length || 0}</span>
        </label>
        <div className="ml-auto font-mono text-xs text-slate-500">
          {elapsedTime.toFixed(2)}s / {duration.toFixed(2)}s
        </div>
      </div>

      <div className="mt-4">
        <input
          type="range"
          min={0}
          max={maxFrame}
          step={1}
          value={currentFrame}
          onChange={(event) => selectFrame(Number(event.target.value))}
          disabled={disabled}
          className="h-2 w-full cursor-pointer accent-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
        />
        <div className="mt-1 flex justify-between font-mono text-[10px] text-slate-600">
          <span>0</span>
          <span>{Math.max(points.length - 1, 0)}</span>
        </div>
      </div>
    </section>
  );
}
