"use client";

import { useEffect, useState } from "react";
import { captionStreamUrl } from "../lib/api";
import type { LiveCaption } from "../lib/types";

export function useCaptionStream(sessionId: string | null, enabled: boolean) {
  const [captions, setCaptions] = useState<LiveCaption[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCaptions([]);
    setError(null);
    if (!sessionId || !enabled) return;

    const url = captionStreamUrl(sessionId);
    const source = new EventSource(url);

    source.addEventListener("caption", (ev) => {
      try {
        const data = JSON.parse((ev as MessageEvent).data) as LiveCaption;
        setCaptions((prev) => [...prev, data]);
      } catch {
        // ignore
      }
    });
    source.addEventListener("error", () => {
      // EventSource reconnects automatically; only surface if it dies hard.
      if (source.readyState === EventSource.CLOSED) {
        setError("Caption stream closed");
      }
    });

    return () => source.close();
  }, [sessionId, enabled]);

  return { captions, error };
}
