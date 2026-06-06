"use client";

import { useEffect, useState } from "react";
import { CaptionStream } from "./components/CaptionStream";
import { RecordingControls } from "./components/RecordingControls";
import { SessionCard } from "./components/SessionCard";
import { useActiveSession } from "./hooks/useActiveSession";
import { useRobotState } from "./hooks/useRobotState";
import { startRecording, stopRecording } from "./lib/api";

export default function CollectionPage() {
  const { data: session, error } = useActiveSession();
  const robot = useRobotState();
  const [working, setWorking] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);

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
          state={robot}
          session={session}
          onStart={handleStart}
          onStop={handleStop}
          isWorking={working}
        />
        {actionError && <p className="mt-2 text-sm text-bad">⚠ {actionError}</p>}
      </div>

      <aside className="min-h-0 flex flex-col gap-4 overflow-y-auto pr-1">
        {error && (
          <div className="rounded-md bg-bad/10 border border-bad/40 text-bad text-sm p-3">
            Backend unreachable: {error}
          </div>
        )}
        {!session && !error && (
          <div className="rounded-md bg-panel border border-slate-800 text-slate-400 text-sm p-3">
            Loading active session…
          </div>
        )}
        {session && <SessionCard session={session} />}
        <div className="flex-1 min-h-[320px]">
          <CaptionStream session={session} recording={recording} />
        </div>
      </aside>
    </main>
  );
}
