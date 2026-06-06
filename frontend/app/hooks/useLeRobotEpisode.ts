"use client";

import { useEffect, useState } from "react";
import { getLeRobotEpisode, getLeRobotEpisodes, getLeRobotInfo } from "../lib/api";
import type { LeRobotEpisodeData, LeRobotEpisodeSummary, LeRobotInfo } from "../lib/types";

export function useLeRobotIndex() {
  const [info, setInfo] = useState<LeRobotInfo | null>(null);
  const [episodes, setEpisodes] = useState<LeRobotEpisodeSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getLeRobotInfo(), getLeRobotEpisodes()])
      .then(([i, eps]) => {
        if (cancelled) return;
        setInfo(i);
        setEpisodes(eps);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { info, episodes, error };
}

export function useLeRobotEpisode(episodeIndex: number | null) {
  const [data, setData] = useState<LeRobotEpisodeData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (episodeIndex === null) {
      setData(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    getLeRobotEpisode(episodeIndex)
      .then((d) => {
        if (!cancelled) {
          setData(d);
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
  }, [episodeIndex]);

  return { data, error, loading };
}
