import type { EpisodeSummary } from "../lib/types";

type Props = {
  episodes: EpisodeSummary[];
  activeId: string | null;
  onSelect: (id: string) => void;
};

export function EpisodeList({ episodes, activeId, onSelect }: Props) {
  return (
    <ul className="space-y-2">
      {episodes.map((ep) => {
        const active = ep.id === activeId;
        return (
          <li key={ep.id}>
            <button
              onClick={() => onSelect(ep.id)}
              className={`w-full text-left rounded-lg border p-3 transition ${
                active
                  ? "border-accent bg-accent/10"
                  : "border-slate-800 bg-panel hover:border-slate-600"
              }`}
            >
              <p className="font-mono text-xs text-slate-500">{ep.id}</p>
              <p className="text-sm font-medium leading-snug mt-1">{ep.title}</p>
              <p className="text-xs text-slate-400 mt-1">
                {ep.duration_s.toFixed(1)}s · {ep.frame_count} frames
              </p>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
