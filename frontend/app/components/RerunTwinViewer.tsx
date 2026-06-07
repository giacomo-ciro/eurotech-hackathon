"use client";

import { useEffect, useRef, useState } from "react";
import type {
  RecordingOpenEvent,
  TimeUpdateEvent,
  WebViewer,
} from "@rerun-io/web-viewer";

type Props = {
  rrdUrl: string;
  currentTime: number;
  onTimeChange: (time: number) => void;
  task?: string;
  jointUnits?: string;
  heightClassName?: string;
};

const TIMELINE = "trajectory";
const NS_PER_SECOND = 1_000_000_000;

function secondsToNanoseconds(seconds: number): number {
  return Math.round(seconds * NS_PER_SECOND);
}

function nanosecondsToSeconds(nanoseconds: number): number {
  return nanoseconds / NS_PER_SECOND;
}

export function RerunTwinViewer({
  rrdUrl,
  currentTime,
  onTimeChange,
  task,
  jointUnits = "degrees",
  heightClassName = "h-[520px]",
}: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<WebViewer | null>(null);
  const recordingIdRef = useRef<string | null>(null);
  const currentTimeRef = useRef(currentTime);
  const onTimeChangeRef = useRef(onTimeChange);
  const lastSetTimeRef = useRef<number | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  currentTimeRef.current = currentTime;
  onTimeChangeRef.current = onTimeChange;

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    let cancelled = false;
    let viewer: WebViewer | null = null;
    const disposers: Array<() => void> = [];

    setStatus("loading");
    setError(null);
    recordingIdRef.current = null;
    lastSetTimeRef.current = null;
    mount.replaceChildren();

    async function startViewer() {
      try {
        const { WebViewer } = await import("@rerun-io/web-viewer");
        if (cancelled) return;

        viewer = new WebViewer();
        viewerRef.current = viewer;

        disposers.push(
          viewer.on("recording_open", (event: RecordingOpenEvent) => {
            if (cancelled || !viewer) return;
            recordingIdRef.current = event.recording_id;

            try {
              viewer.set_active_recording_id(event.recording_id);
              viewer.set_active_timeline(event.recording_id, TIMELINE);
              viewer.set_playing(event.recording_id, false);
              const timeNs = secondsToNanoseconds(currentTimeRef.current);
              lastSetTimeRef.current = timeNs;
              viewer.set_current_time(event.recording_id, TIMELINE, timeNs);
              viewer.override_panel_state("blueprint", "hidden");
              viewer.override_panel_state("selection", "hidden");
              viewer.override_panel_state("time", "hidden");
              viewer.override_panel_state("top", "collapsed");
              viewer.toggle_panel_overrides(true);
            } catch (err) {
              console.warn("Failed to initialize Rerun viewer controls", err);
            }

            setStatus("ready");
          }),
        );

        disposers.push(
          viewer.on("time_update", (event: TimeUpdateEvent) => {
            if (cancelled || !viewer) return;
            const activeTimeline = viewer.get_active_timeline(event.recording_id);
            if (activeTimeline && activeTimeline !== TIMELINE) return;

            const seconds = nanosecondsToSeconds(event.time);
            if (!Number.isFinite(seconds)) return;

            const lastSetTime = lastSetTimeRef.current;
            if (lastSetTime !== null && Math.abs(event.time - lastSetTime) < 1_000_000) {
              return;
            }
            if (Math.abs(seconds - currentTimeRef.current) > 0.015) {
              onTimeChangeRef.current(seconds);
            }
          }),
        );

        await viewer.start(rrdUrl, mount, {
          hide_welcome_screen: true,
          render_backend: "webgl",
          width: "100%",
          height: "100%",
        });
      } catch (err) {
        if (cancelled) return;
        setStatus("error");
        setError(err instanceof Error ? err.message : String(err));
      }
    }

    void startViewer();

    return () => {
      cancelled = true;
      disposers.forEach((dispose) => dispose());
      if (viewerRef.current === viewer) viewerRef.current = null;
      recordingIdRef.current = null;
      try {
        viewer?.stop();
      } catch (err) {
        console.warn("Failed to stop Rerun viewer", err);
      }
      mount.replaceChildren();
    };
  }, [rrdUrl]);

  useEffect(() => {
    const viewer = viewerRef.current;
    const recordingId = recordingIdRef.current;
    if (!viewer || !recordingId || status !== "ready") return;

    const timeNs = secondsToNanoseconds(currentTime);
    lastSetTimeRef.current = timeNs;
    try {
      viewer.set_active_timeline(recordingId, TIMELINE);
      viewer.set_current_time(recordingId, TIMELINE, timeNs);
    } catch (err) {
      console.warn("Failed to sync Rerun time", err);
    }
  }, [currentTime, status]);

  return (
    <section className="overflow-hidden rounded-lg border border-slate-800 bg-panel">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-4 py-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">Digital twin</p>
          <h3 className="mt-1 text-sm font-semibold text-slate-100">SO-101 trajectory replay</h3>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
          {task ? (
            <span className="rounded-full border border-slate-700 px-2 py-1 text-slate-200">
              {task}
            </span>
          ) : null}
          <span className="rounded-full border border-slate-700 px-2 py-1">
            joints: {jointUnits}
          </span>
        </div>
      </div>
      <div className={`relative min-h-[360px] bg-black ${heightClassName}`}>
        <div
          ref={mountRef}
          className="absolute inset-0 [&>canvas]:block [&>canvas]:h-full [&>canvas]:w-full"
        />
        {status !== "ready" ? (
          <div className="pointer-events-none absolute inset-0 grid place-items-center bg-slate-950/80 px-4 text-center">
            <div>
              <p className="text-sm font-semibold text-slate-200">
                {status === "error" ? "Unable to load Rerun trajectory" : "Loading Rerun trajectory…"}
              </p>
              {error ? <p className="mt-2 max-w-xl text-xs text-slate-500">{error}</p> : null}
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
