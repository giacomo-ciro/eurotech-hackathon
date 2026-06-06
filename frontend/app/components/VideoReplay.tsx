"use client";

import { useEffect, useRef } from "react";

type Props = {
  src: string;
  onTimeUpdate: (t: number) => void;
};

export function VideoReplay({ src, onTimeUpdate }: Props) {
  const ref = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handler = () => onTimeUpdate(el.currentTime);
    el.addEventListener("timeupdate", handler);
    el.addEventListener("seeking", handler);
    return () => {
      el.removeEventListener("timeupdate", handler);
      el.removeEventListener("seeking", handler);
    };
  }, [onTimeUpdate]);

  // Reset playback when src changes
  useEffect(() => {
    if (ref.current) ref.current.currentTime = 0;
    onTimeUpdate(0);
  }, [src, onTimeUpdate]);

  return (
    <div className="rounded-xl overflow-hidden bg-black border border-slate-800 aspect-video relative">
      <video
        ref={ref}
        src={src}
        controls
        className="absolute inset-0 w-full h-full object-contain"
      />
      <div className="absolute bottom-1 left-2 text-[10px] font-mono text-slate-400 pointer-events-none">
        If the player is empty, drop a real .mp4 at <span className="text-accent">data/datasets/&lt;id&gt;/episodes/&lt;ep&gt;/video.mp4</span>
      </div>
    </div>
  );
}
