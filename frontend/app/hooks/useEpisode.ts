"use client";

import { useEffect, useState } from "react";
import { getEpisode } from "../lib/api";
import type { Episode } from "../lib/types";

export function useEpisode(datasetId: string | null, episodeId: string | null) {
  const [data, setData] = useState<Episode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!datasetId || !episodeId) {
      setData(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    getEpisode(datasetId, episodeId)
      .then((ep) => {
        if (!cancelled) {
          setData(ep);
          setError(null);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [datasetId, episodeId]);

  return { data, error, loading };
}
