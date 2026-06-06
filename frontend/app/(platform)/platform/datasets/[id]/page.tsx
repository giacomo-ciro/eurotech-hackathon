"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CaptionTrack } from "../../../../components/CaptionTrack";
import { EpisodeList } from "../../../../components/EpisodeList";
import { TimeseriesChart } from "../../../../components/TimeseriesChart";
import { VideoReplay } from "../../../../components/VideoReplay";
import { useEpisode } from "../../../../hooks/useEpisode";
import { episodeVideoUrl, getDataset } from "../../../../lib/api";
import type { DatasetDetail } from "../../../../lib/types";

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
            <span>Episodes: <span className="text-slate-200">{detail.episode_count}</span></span>
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

      <div className="grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)] gap-4">
        <aside>
          <h3 className="text-xs uppercase tracking-widest text-slate-400 mb-2">Episodes</h3>
          <EpisodeList
            episodes={detail.episodes}
            activeId={episodeId}
            onSelect={(id) => {
              setEpisodeId(id);
              setCurrentTime(0);
            }}
          />
        </aside>

        <section className="space-y-4 min-w-0">
          {!episode && episodeId && <p className="text-slate-500 text-sm">Loading episode…</p>}
          {episode && (
            <>
              <div>
                <p className="text-xs font-mono text-slate-500">{episode.id}</p>
                <h2 className="text-lg font-semibold leading-tight">{episode.title}</h2>
              </div>
              <VideoReplay
                src={episodeVideoUrl(datasetId, episode.id)}
                onTimeUpdate={setCurrentTime}
              />
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                <TimeseriesChart points={episode.timeseries} currentTime={currentTime} />
                <CaptionTrack captions={episode.captions} currentTime={currentTime} />
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
