"use client";

import { useEffect, useState } from "react";
import { getActivePrescription } from "../lib/api";
import type { ActivePrescriptionDetail } from "../lib/types";

export function useActivePrescription(pollMs: number = 3000) {
  const [data, setData] = useState<ActivePrescriptionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function tick() {
      try {
        const fresh = await getActivePrescription();
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

  return { data, error };
}
