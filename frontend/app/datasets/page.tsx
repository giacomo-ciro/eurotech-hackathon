"use client";

import { useEffect, useState } from "react";
import { DatasetGrid } from "../components/DatasetGrid";
import { getDatasets } from "../lib/api";
import type { Dataset } from "../lib/types";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getDatasets()
      .then((rows) => {
        if (!cancelled) setDatasets(rows);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="flex-1 overflow-y-auto p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Marketplace</h1>
        <p className="text-slate-400 text-sm mt-1">
          Browse Claude-augmented LeRobot datasets ready for SmolVLA fine-tuning.
        </p>
      </header>

      {error && (
        <div className="rounded-md bg-bad/10 border border-bad/40 text-bad text-sm p-3 mb-4">
          Backend unreachable: {error}
        </div>
      )}
      {!datasets && !error && <p className="text-slate-400 text-sm">Loading datasets…</p>}
      {datasets && <DatasetGrid datasets={datasets} />}
    </main>
  );
}
