"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { streamChat } from "../lib/api";
import { useCaptionStream } from "../hooks/useCaptionStream";
import type { ChatMessage, LiveCaption, Session } from "../lib/types";

type Entry =
  | { kind: "caption"; t: number; text: string }
  | { kind: "chat-user"; text: string }
  | { kind: "chat-assistant"; text: string };

type Props = {
  session: Session | null;
  recording: boolean;
};

export function CaptionStream({ session, recording }: Props) {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [draft, setDraft] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const sessionId = session?.id ?? null;
  const { captions } = useCaptionStream(sessionId, recording);

  useEffect(() => {
    setEntries([]);
    setErrorMsg(null);
  }, [sessionId]);

  const lastCaptionIndex = useRef(0);
  useEffect(() => {
    if (captions.length <= lastCaptionIndex.current) return;
    const fresh = captions.slice(lastCaptionIndex.current);
    lastCaptionIndex.current = captions.length;
    setEntries((prev) => [
      ...prev,
      ...fresh.map((c: LiveCaption): Entry => ({ kind: "caption", t: c.t, text: c.text })),
    ]);
  }, [captions]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [entries, streaming]);

  const chatHistory: ChatMessage[] = useMemo(
    () =>
      entries
        .filter((e) => e.kind === "chat-user" || e.kind === "chat-assistant")
        .map((e) =>
          e.kind === "chat-user"
            ? { role: "user", content: e.text }
            : { role: "assistant", content: e.text },
        ),
    [entries],
  );

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || streaming || !session) return;

    setEntries((prev) => [
      ...prev,
      { kind: "chat-user", text: trimmed },
      { kind: "chat-assistant", text: "" },
    ]);
    setDraft("");
    setStreaming(true);
    setErrorMsg(null);

    const messages: ChatMessage[] = [
      ...chatHistory,
      { role: "user", content: trimmed },
    ];

    const controller = new AbortController();
    await streamChat(
      messages,
      { session_id: session.id },
      {
        onToken: (chunk) => {
          setEntries((prev) => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            if (last && last.kind === "chat-assistant") {
              copy[copy.length - 1] = { ...last, text: last.text + chunk };
            }
            return copy;
          });
        },
        onDone: () => setStreaming(false),
        onError: (msg) => {
          setErrorMsg(msg);
          setStreaming(false);
        },
      },
      controller.signal,
    );
  }

  return (
    <section className="rounded-xl bg-panel border border-slate-800 p-4 flex flex-col h-full min-h-0">
      <header className="flex items-center justify-between mb-3">
        <h3 className="text-xs uppercase tracking-widest text-slate-400">
          Auto-captions + chat
        </h3>
        <span className="text-xs font-mono text-slate-500">
          {recording ? "● live" : "○ idle"}
        </span>
      </header>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto rounded-md bg-slate-900/40 border border-slate-800 p-3 space-y-3 min-h-[200px]"
      >
        {entries.length === 0 && (
          <p className="text-sm text-slate-500 italic">
            {recording
              ? "Streaming Claude captions for the active trajectory…"
              : "Start recording to see Claude generate synthetic captions in real time. You can also ask Claude questions about the session below."}
          </p>
        )}
        {entries.map((entry, idx) => {
          if (entry.kind === "caption") {
            return (
              <div key={idx} className="text-sm leading-relaxed text-slate-300">
                <span className="text-[10px] uppercase tracking-widest mr-2 font-mono text-warn">
                  caption · t={entry.t.toFixed(1)}s
                </span>
                <span className="whitespace-pre-wrap">{entry.text}</span>
              </div>
            );
          }
          return (
            <div
              key={idx}
              className={`text-sm leading-relaxed ${
                entry.kind === "chat-user" ? "text-slate-200" : "text-slate-300"
              }`}
            >
              <span
                className={`text-[10px] uppercase tracking-widest mr-2 font-mono ${
                  entry.kind === "chat-user" ? "text-accent" : "text-ok"
                }`}
              >
                {entry.kind === "chat-user" ? "you" : "claude"}
              </span>
              <span className="whitespace-pre-wrap">
                {entry.text || (streaming && idx === entries.length - 1 ? "…" : "")}
              </span>
            </div>
          );
        })}
        {errorMsg && <p className="text-sm text-bad">⚠ {errorMsg}</p>}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(draft);
        }}
        className="mt-3 flex gap-2"
      >
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={session ? "Ask Claude about this session…" : "No active session"}
          className="flex-1 rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-accent"
          disabled={streaming || !session}
        />
        <button
          type="submit"
          disabled={streaming || !draft.trim() || !session}
          className="rounded-md bg-accent text-ink font-semibold px-4 text-sm disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </section>
  );
}
