import Link from "next/link";
import { datasetCoverUrl } from "../lib/api";
import type { Dataset } from "../lib/types";

const STATUS_COLORS: Record<string, string> = {
  raw: "bg-slate-500/20 text-slate-300 border-slate-500/40",
  augmented: "bg-accent/20 text-accent border-accent/50",
  "fine-tuned": "bg-ok/20 text-ok border-ok/50",
};

export function DatasetCard({ dataset }: { dataset: Dataset }) {
  const pill = STATUS_COLORS[dataset.augmentation_status] ?? STATUS_COLORS.raw;
  return (
    <Link
      href={`/datasets/${dataset.id}`}
      className="group rounded-xl bg-panel border border-slate-800 overflow-hidden hover:border-accent/60 transition flex flex-col"
    >
      <div className="aspect-video bg-slate-900 overflow-hidden">
        <img
          src={datasetCoverUrl(dataset.id)}
          alt={dataset.name}
          className="w-full h-full object-cover group-hover:scale-[1.02] transition"
        />
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-base font-semibold leading-tight">{dataset.name}</h3>
          <span
            className={`shrink-0 text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full border ${pill}`}
          >
            {dataset.augmentation_status}
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1 line-clamp-2">{dataset.description}</p>
        <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1 text-xs text-slate-400">
          <div className="flex justify-between"><dt>Domain</dt><dd className="text-slate-200">{dataset.domain}</dd></div>
          <div className="flex justify-between"><dt>Robot</dt><dd className="text-slate-200">{dataset.robot}</dd></div>
          <div className="flex justify-between"><dt>Episodes</dt><dd className="text-slate-200">{dataset.episode_count}</dd></div>
          <div className="flex justify-between"><dt>Frames</dt><dd className="text-slate-200">{dataset.frame_count.toLocaleString()}</dd></div>
        </dl>
        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-slate-500">{dataset.size_mb.toFixed(1)} MB</span>
          <span className="text-accent font-semibold">
            ${dataset.price_usd.toLocaleString()}
          </span>
        </div>
      </div>
    </Link>
  );
}
