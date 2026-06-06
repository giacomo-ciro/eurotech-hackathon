"use client";

import { useEffect, useState } from "react";
import { getActiveSession } from "../lib/api";
import type { Session } from "../lib/types";

export function useActiveSession(pollMs: number = 3000) {
  const [data, setData] = useState<Session | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function tick() {
      try {
        const fresh = await getActiveSession();
        if (!cancelled) {
          setData(fresh);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    }

    tick();
    const handle = window.setInterval(tick, pollMs);
    return () => {
      cancelled = true;
      window.clearInterval(handle);
    };
  }, [pollMs]);

  return { data, error, refresh: async () => setData(await getActiveSession()) };
}
