"use client";

import { useEffect, useMemo, useRef } from "react";
import { RERUN_URL, lerobotVideoUrl } from "../lib/api";
import type {
  LeRobotEpisodeData,
  LeRobotEpisodeSummary,
  RobotStateEvent,
  Session,
  VideoMode,
} from "../lib/types";

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
  mode: VideoMode;
  onModeChange: (mode: VideoMode) => void;

  // live
  state: RobotStateEvent;
  session: Session | null;
  onStart: () => void;
  onStop: () => void;
  isWorking: boolean;

  // recorded
  episodes: LeRobotEpisodeSummary[];
  selectedEpisode: number | null;
  episodeData: LeRobotEpisodeData | null;
  onSelectEpisode: (idx: number) => void;
  onPlaybackTime: (t: number) => void;
  autoplay: boolean;
  onToggleAutoplay: () => void;
  onPrev: () => void;
  onNext: () => void;
};

export function RecordingControls({
  mode,
  onModeChange,
  state,
  session,
  onStart,
  onStop,
  isWorking,
  episodes,
  selectedEpisode,
  episodeData,
  onSelectEpisode,
  onPlaybackTime,
  autoplay,
  onToggleAutoplay,
  onPrev,
  onNext,
}: Props) {
  return (
    <section className="flex flex-col gap-4 h-full">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className={`inline-block h-2.5 w-2.5 rounded-full ${
              mode === "recorded" ? "bg-warn" : stageColor(state)
            }`}
          />
          <h2 className="text-lg font-semibold tracking-tight">Robot stream</h2>
        </div>
        <ModeToggle mode={mode} onChange={onModeChange} />
      </div>

      {mode === "live" ? (
        <LiveView state={state} />
      ) : (
        <RecordedView
          episodes={episodes}
          selectedEpisode={selectedEpisode}
          episodeData={episodeData}
          onSelectEpisode={onSelectEpisode}
          onPlaybackTime={onPlaybackTime}
          autoplay={autoplay}
          onToggleAutoplay={onToggleAutoplay}
          onPrev={onPrev}
          onNext={onNext}
        />
      )}

      {mode === "live" && (
        <LiveControls
          state={state}
          session={session}
          onStart={onStart}
          onStop={onStop}
          isWorking={isWorking}
        />
      )}
    </section>
  );
}

function ModeToggle({
  mode,
  onChange,
}: {
  mode: VideoMode;
  onChange: (mode: VideoMode) => void;
}) {
  return (
    <div className="inline-flex rounded-full border border-slate-700 bg-slate-900/60 p-0.5 text-xs">
      {(["live", "recorded"] as VideoMode[]).map((m) => (
        <button
          key={m}
          onClick={() => onChange(m)}
          className={`px-3 py-1 rounded-full uppercase tracking-widest transition ${
            mode === m ? "bg-accent text-ink font-semibold" : "text-slate-300 hover:text-slate-100"
          }`}
        >
          {m}
        </button>
      ))}
    </div>
  );
}

function LiveView({ state }: { state: RobotStateEvent }) {
  return (
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
              Start with:{" "}
              <span className="text-accent">uv run python -m robot_bridge.app.main</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function LiveControls({
  state,
  session,
  onStart,
  onStop,
  isWorking,
}: {
  state: RobotStateEvent;
  session: Session | null;
  onStart: () => void;
  onStop: () => void;
  isWorking: boolean;
}) {
  const activeIndex = useMemo(() => {
    if (state.stage in STAGE_INDEX) return STAGE_INDEX[state.stage];
    return -1;
  }, [state.stage]);
  const canStart = !!session && state.stage !== "offline" && state.stage !== "recording";
  const canStop = state.stage === "recording" || state.stage === "captioning";

  return (
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
  );
}

function RecordedView({
  episodes,
  selectedEpisode,
  episodeData,
  onSelectEpisode,
  onPlaybackTime,
  autoplay,
  onToggleAutoplay,
  onPrev,
  onNext,
}: {
  episodes: LeRobotEpisodeSummary[];
  selectedEpisode: number | null;
  episodeData: LeRobotEpisodeData | null;
  onSelectEpisode: (idx: number) => void;
  onPlaybackTime: (t: number) => void;
  autoplay: boolean;
  onToggleAutoplay: () => void;
  onPrev: () => void;
  onNext: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const advancingRef = useRef(false);

  // When episodeData changes, seek to its start; autoplay if requested.
  useEffect(() => {
    const el = videoRef.current;
    if (!el || !episodeData) return;
    advancingRef.current = false;
    el.currentTime = episodeData.video_from_s;
    onPlaybackTime(0);
    if (autoplay) {
      el.play().catch(() => {
        // Browsers reject programmatic play() during reloads or before user
        // interaction; the controls let the operator resume manually.
      });
    }
  }, [episodeData, autoplay, onPlaybackTime]);

  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;
    const handler = () => {
      const t = el.currentTime;
      if (episodeData) {
        if (t >= episodeData.video_to_s) {
          if (autoplay) {
            if (advancingRef.current) return;
            advancingRef.current = true;
            onNext();
          } else {
            el.pause();
            el.currentTime = episodeData.video_to_s;
            onPlaybackTime(episodeData.video_to_s - episodeData.video_from_s);
          }
          return;
        }
        if (t < episodeData.video_from_s) {
          el.currentTime = episodeData.video_from_s;
          onPlaybackTime(0);
          return;
        }
        onPlaybackTime(t - episodeData.video_from_s);
      } else {
        onPlaybackTime(t);
      }
    };
    el.addEventListener("timeupdate", handler);
    el.addEventListener("seeking", handler);
    return () => {
      el.removeEventListener("timeupdate", handler);
      el.removeEventListener("seeking", handler);
    };
  }, [episodeData, autoplay, onNext, onPlaybackTime]);

  const source = selectedEpisode !== null ? lerobotVideoUrl(selectedEpisode) : null;
  const noEpisodes = episodes.length === 0;

  return (
    <div className="flex flex-col gap-2 flex-1 min-h-0">
      <div className="flex flex-wrap items-center gap-2">
        <label className="text-xs uppercase tracking-widest text-slate-400">Episode</label>
        <select
          value={selectedEpisode ?? ""}
          onChange={(e) => onSelectEpisode(Number(e.target.value))}
          className="bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:border-accent"
        >
          {noEpisodes && <option value="">No LeRobot dataset loaded</option>}
          {episodes.map((ep) => (
            <option key={ep.episode_index} value={ep.episode_index}>
              #{ep.episode_index.toString().padStart(2, "0")} · {ep.task} · {ep.length_frames}f · {ep.duration_s.toFixed(1)}s
            </option>
          ))}
        </select>
        <button
          onClick={onPrev}
          disabled={noEpisodes}
          className="rounded-md border border-slate-700 text-slate-200 px-2.5 py-1.5 text-sm hover:border-slate-500 disabled:opacity-40 disabled:cursor-not-allowed"
          title="Previous episode"
        >
          ‹ Prev
        </button>
        <button
          onClick={onNext}
          disabled={noEpisodes}
          className="rounded-md border border-slate-700 text-slate-200 px-2.5 py-1.5 text-sm hover:border-slate-500 disabled:opacity-40 disabled:cursor-not-allowed"
          title="Next episode"
        >
          Next ›
        </button>
        <button
          onClick={onToggleAutoplay}
          className={`ml-auto rounded-full border px-3 py-1 text-xs uppercase tracking-widest transition ${
            autoplay
              ? "border-accent bg-accent/15 text-accent"
              : "border-slate-700 text-slate-300 hover:border-slate-500"
          }`}
          title="Autoplay next episode"
        >
          ● Autoplay {autoplay ? "on" : "off"}
        </button>
      </div>

      {episodeData && (
        <span className="text-xs font-mono text-slate-500">
          clip {episodeData.video_from_s.toFixed(1)}s → {episodeData.video_to_s.toFixed(1)}s · {episodeData.fps}fps
        </span>
      )}

      <div className="relative flex-1 rounded-2xl overflow-hidden bg-black border border-slate-800 shadow-2xl">
        {source ? (
          <video
            ref={videoRef}
            src={source}
            controls
            className="absolute inset-0 h-full w-full object-contain"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm">
            Pick an episode to play.
          </div>
        )}
      </div>
      <p className="text-[11px] text-slate-500">
        Source is AV1 — works in Chrome / Edge / Firefox. Safari shows a blank player.
      </p>
    </div>
  );
}
