"use client";

import { useEffect, useState } from "react";
import { CaptionStream } from "../../components/CaptionStream";
import { EpisodeDataPanel } from "../../components/EpisodeDataPanel";
import { RecordingControls } from "../../components/RecordingControls";
import { SessionCard } from "../../components/SessionCard";
import { useActiveSession } from "../../hooks/useActiveSession";
import { useLeRobotEpisode, useLeRobotIndex } from "../../hooks/useLeRobotEpisode";
import { useRobotState } from "../../hooks/useRobotState";
import { startRecording, stopRecording } from "../../lib/api";
import type { VideoMode } from "../../lib/types";

export default function CollectionPage() {
  const { data: session, error } = useActiveSession();
  const robot = useRobotState();
  const [working, setWorking] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);

  const [mode, setMode] = useState<VideoMode>("live");
  const { episodes, error: lerobotError } = useLeRobotIndex();
  const [selectedEpisode, setSelectedEpisode] = useState<number | null>(null);
  const { data: episodeData } = useLeRobotEpisode(
    mode === "recorded" ? selectedEpisode : null,
  );
  const [episodeTime, setEpisodeTime] = useState(0);
  const [autoplay, setAutoplay] = useState(true);

  // Auto-select the first episode the first time the user flips to Recorded.
  useEffect(() => {
    if (mode === "recorded" && selectedEpisode === null && episodes.length > 0) {
      setSelectedEpisode(episodes[0].episode_index);
    }
  }, [mode, selectedEpisode, episodes]);

  function stepEpisode(direction: 1 | -1) {
    if (episodes.length === 0) return;
    const currentPos = episodes.findIndex(
      (ep) => ep.episode_index === selectedEpisode,
    );
    const base = currentPos === -1 ? 0 : currentPos;
    const nextPos = (base + direction + episodes.length) % episodes.length;
    setSelectedEpisode(episodes[nextPos].episode_index);
    setEpisodeTime(0);
  }

  useEffect(() => {
    if (robot.stage === "recording" || robot.stage === "captioning") {
      setRecording(true);
    } else if (robot.stage === "saved" || robot.stage === "idle" || robot.stage === "offline") {
      setRecording(false);
    }
  }, [robot.stage]);

  async function handleStart() {
    if (!session) return;
    setWorking(true);
    setActionError(null);
    try {
      await startRecording(session.id);
      setRecording(true);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : String(err));
    } finally {
      window.setTimeout(() => setWorking(false), 1500);
    }
  }

  async function handleStop() {
    if (!session) return;
    setWorking(true);
    setActionError(null);
    try {
      await stopRecording(session.id);
      setRecording(false);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : String(err));
    } finally {
      setWorking(false);
    }
  }

  return (
    <main className="flex-1 grid grid-cols-1 lg:grid-cols-[minmax(0,1.4fr)_minmax(360px,1fr)] gap-4 p-6 overflow-hidden">
      <div className="min-h-0 flex flex-col">
        <RecordingControls
          mode={mode}
          onModeChange={(m) => {
            setMode(m);
            setEpisodeTime(0);
          }}
          state={robot}
          session={session}
          onStart={handleStart}
          onStop={handleStop}
          isWorking={working}
          episodes={episodes}
          selectedEpisode={selectedEpisode}
          episodeData={episodeData}
          onSelectEpisode={(idx) => {
            setSelectedEpisode(idx);
            setEpisodeTime(0);
          }}
          onPlaybackTime={setEpisodeTime}
          autoplay={autoplay}
          onToggleAutoplay={() => setAutoplay((v) => !v)}
          onPrev={() => stepEpisode(-1)}
          onNext={() => stepEpisode(1)}
        />
        {actionError && <p className="mt-2 text-sm text-bad">⚠ {actionError}</p>}
        {mode === "recorded" && lerobotError && (
          <p className="mt-2 text-sm text-bad">
            ⚠ LeRobot dataset unavailable: {lerobotError}
          </p>
        )}
      </div>

      <aside className="min-h-0 flex flex-col gap-4 overflow-y-auto pr-1">
        {error && (
          <div className="rounded-md bg-bad/10 border border-bad/40 text-bad text-sm p-3">
            Backend unreachable: {error}
          </div>
        )}

        {mode === "live" && (
          <>
            {!session && !error && (
              <div className="rounded-md bg-panel border border-slate-800 text-slate-400 text-sm p-3">
                Loading active session…
              </div>
            )}
            {session && <SessionCard session={session} />}
            <div className="flex-1 min-h-[320px]">
              <CaptionStream session={session} recording={recording} />
            </div>
          </>
        )}

        {mode === "recorded" && (
          <>
            <EpisodeDataPanel data={episodeData} episodeTime={episodeTime} />
            <div className="rounded-xl bg-panel border border-slate-800 p-4 text-sm text-slate-400 leading-relaxed">
              <h3 className="text-xs uppercase tracking-widest text-slate-400 mb-2">
                Inspect mode
              </h3>
              <p>
                You are viewing a recorded LeRobot episode. The bars show each joint's
                <span className="text-accent"> action target</span> with the
                <span className="text-ok"> observed state</span> overlaid. Scrub the video to
                move through the trajectory.
              </p>
            </div>
          </>
        )}
      </aside>
    </main>
  );
}
