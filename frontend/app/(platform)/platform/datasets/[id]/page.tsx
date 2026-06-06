"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { CaptionTrack } from "../../components/CaptionTrack";
import { DigitalTwinViewer } from "../../components/DigitalTwinViewer";
import { TimeseriesChart } from "../../components/TimeseriesChart";
import { TrajectoryPlaybackControls } from "../../components/TrajectoryPlaybackControls";
import { useEpisode } from "../../hooks/useEpisode";
import { getDataset } from "../../lib/api";
import type { DatasetDetail } from "../../lib/types";

type Props = { params: { id: string } };

const STATUS_COLORS: Record<string, string> = {
  raw: "bg-slate-500/20 text-slate-300 border-slate-500/40",
  augmented: "bg-accent/20 text-accent border-accent/50",
  "fine-tuned": "bg-ok/20 text-ok border-ok/50",
};

export default function DatasetDetailPage({ params }: Props) {
  const datasetId = params.id;
  const [detail, setDetail] = useState<DatasetDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [episodeId, setEpisodeId] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);

  const { data: episode } = useEpisode(datasetId, episodeId);
  const activeTrajectoryIndex = useMemo(() => {
    if (!detail || !episodeId) return 0;
    const index = detail.episodes.findIndex((ep) => ep.id === episodeId);
    return index >= 0 ? index : 0;
  }, [detail, episodeId]);

  useEffect(() => {
    let cancelled = false;
    getDataset(datasetId)
      .then((d) => {
        if (cancelled) return;
        setDetail(d);
        if (d.episodes.length > 0) setEpisodeId(d.episodes[0].id);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  if (error) {
    return (
      <main className="p-6">
        <div className="rounded-md bg-bad/10 border border-bad/40 text-bad text-sm p-3">
          {error}
        </div>
      </main>
    );
  }
  if (!detail) {
    return <main className="p-6 text-slate-400">Loading dataset…</main>;
  }

  const pill = STATUS_COLORS[detail.augmentation_status] ?? STATUS_COLORS.raw;
  const runCountLabel = detail.id === "imported-lerobot" ? "Trajectories" : "Episodes";

  return (
    <main className="flex-1 overflow-y-auto p-6 space-y-4">
      <div className="text-xs text-slate-500">
        <Link href="/platform/datasets" className="hover:text-accent">← Marketplace</Link>
      </div>

      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{detail.name}</h1>
            <span className={`text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full border ${pill}`}>
              {detail.augmentation_status}
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">{detail.description}</p>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
            <span>Domain: <span className="text-slate-200">{detail.domain}</span></span>
            <span>Robot: <span className="text-slate-200">{detail.robot}</span></span>
            <span>{runCountLabel}: <span className="text-slate-200">{detail.episode_count}</span></span>
            <span>Frames: <span className="text-slate-200">{detail.frame_count.toLocaleString()}</span></span>
            <span>Size: <span className="text-slate-200">{detail.size_mb.toFixed(1)} MB</span></span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-accent">${detail.price_usd.toLocaleString()}</p>
          <button className="mt-2 rounded-lg bg-accent text-ink font-semibold px-4 py-2 hover:bg-accent/90 transition">
            Purchase + download
          </button>
        </div>
      </header>

      <section className="space-y-4 min-w-0">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">Trajectory replay</p>
            <h2 className="mt-1 text-lg font-semibold leading-tight">
              Trajectory {String(activeTrajectoryIndex + 1).padStart(2, "0")}
              {episode?.task ? <span className="text-slate-500"> · {episode.task}</span> : null}
            </h2>
          </div>
          <label className="flex min-w-64 flex-col gap-1 text-xs uppercase tracking-widest text-slate-500">
            Trajectory
            <select
              value={episodeId ?? ""}
              onChange={(event) => {
                setEpisodeId(event.target.value);
                setCurrentTime(0);
              }}
              className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm normal-case tracking-normal text-slate-100 focus:border-accent focus:outline-none"
            >
              {detail.episodes.map((ep, index) => (
                <option key={ep.id} value={ep.id}>
                  {String(index + 1).padStart(2, "0")} · {ep.task || "unlabeled"} · {ep.frame_count} frames
                </option>
              ))}
            </select>
          </label>
        </div>

        {!episode && episodeId && <p className="text-slate-500 text-sm">Loading trajectory…</p>}
        {episode && (
          <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_420px] gap-4 items-start">
            <div className="space-y-4 min-w-0">
              <DigitalTwinViewer
                points={episode.timeseries}
                currentTime={currentTime}
                task={episode.task}
                jointUnits={episode.joint_units}
                heightClassName="h-[420px] md:h-[560px] xl:h-[680px]"
              />
              <TrajectoryPlaybackControls
                points={episode.timeseries}
                currentTime={currentTime}
                onTimeChange={setCurrentTime}
              />
            </div>
            <div className="space-y-4 min-w-0 xl:pt-7">
              <TimeseriesChart
                points={episode.timeseries}
                currentTime={currentTime}
                jointUnits={episode.joint_units}
              />
              {episode.captions.length > 0 && (
                <CaptionTrack captions={episode.captions} currentTime={currentTime} />
              )}
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
