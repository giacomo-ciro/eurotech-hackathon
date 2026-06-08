"use client";

import { useMemo, useState } from "react";
import { DatasetCard } from "./DatasetCard";
import type { AugmentationStatus, Dataset } from "../lib/types";

const STATUSES: AugmentationStatus[] = ["raw", "augmented", "fine-tuned"];

export function DatasetGrid({ datasets }: { datasets: Dataset[] }) {
  const domains = useMemo(
    () => Array.from(new Set(datasets.map((d) => d.domain))).sort(),
    [datasets],
  );

  const [domain, setDomain] = useState<string | null>(null);
  const [status, setStatus] = useState<AugmentationStatus | null>(null);
  const [query, setQuery] = useState("");

  const filtered = datasets.filter((d) => {
    if (domain && d.domain !== domain) return false;
    if (status && d.augmentation_status !== status) return false;
    if (query.trim()) {
      const q = query.toLowerCase();
      if (!d.name.toLowerCase().includes(q) && !d.description.toLowerCase().includes(q))
        return false;
    }
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <input
          placeholder="Search datasets…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm w-72 focus:outline-none focus:border-accent"
        />
        <div className="flex gap-1 flex-wrap">
          <FilterChip label="All domains" active={domain === null} onClick={() => setDomain(null)} />
          {domains.map((d) => (
            <FilterChip key={d} label={d} active={domain === d} onClick={() => setDomain(d)} />
          ))}
        </div>
        <div className="flex gap-1 flex-wrap">
          <FilterChip label="Any status" active={status === null} onClick={() => setStatus(null)} />
          {STATUSES.map((s) => (
            <FilterChip key={s} label={s} active={status === s} onClick={() => setStatus(s)} />
          ))}
        </div>
        <div className="ml-auto text-xs text-slate-500 font-mono">
          {filtered.length} / {datasets.length}
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-slate-500 text-sm italic">No datasets match the current filters.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <DatasetCard key={d.id} dataset={d} />
          ))}
        </div>
      )}
    </div>
  );
}

function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-xs px-2.5 py-1 rounded-full border transition ${
        active
          ? "border-accent text-accent bg-accent/10"
          : "border-slate-700 text-slate-400 hover:border-slate-500"
      }`}
    >
      {label}
    </button>
  );
}
