"use client";

import { useEffect, useRef, useState } from "react";
import { streamChat } from "../lib/api";
import type { ChatMessage, Medicine } from "../lib/types";

const SUGGESTIONS = [
  "What are the side effects?",
  "Can it be taken with food?",
  "Any interaction with warfarin?",
  "請用繁體中文解釋服用方法",
];

type Props = { medicine: Medicine };

export function ChatPanel({ medicine }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setMessages([]);
    setErrorMsg(null);
  }, [medicine.drug_id]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streaming]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || streaming) return;

    const next: ChatMessage[] = [...messages, { role: "user", content: trimmed }];
    setMessages([...next, { role: "assistant", content: "" }]);
    setDraft("");
    setStreaming(true);
    setErrorMsg(null);

    const controller = new AbortController();
    await streamChat(
      medicine.drug_id,
      next,
      {
        onToken: (chunk) => {
          setMessages((prev) => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            if (last && last.role === "assistant") {
              copy[copy.length - 1] = { ...last, content: last.content + chunk };
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
          Ask about {medicine.drug_name}
        </h3>
        <span className="text-xs font-mono text-slate-500">claude · grounded</span>
      </header>

      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            disabled={streaming}
            className="text-xs px-2 py-1 rounded-full border border-slate-700 hover:border-accent hover:text-accent transition disabled:opacity-40"
          >
            {s}
          </button>
        ))}
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto rounded-md bg-slate-900/40 border border-slate-800 p-3 space-y-3 min-h-[200px]"
      >
        {messages.length === 0 && (
          <p className="text-sm text-slate-500 italic">
            Ask anything grounded in this medicine's catalog entry and known interactions.
          </p>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`text-sm leading-relaxed ${
              msg.role === "user" ? "text-slate-200" : "text-slate-300"
            }`}
          >
            <span
              className={`text-[10px] uppercase tracking-widest mr-2 font-mono ${
                msg.role === "user" ? "text-accent" : "text-ok"
              }`}
            >
              {msg.role === "user" ? "you" : "claude"}
            </span>
            <span className="whitespace-pre-wrap">{msg.content || (streaming && idx === messages.length - 1 ? "…" : "")}</span>
          </div>
        ))}
        {errorMsg && (
          <p className="text-sm text-bad">⚠ {errorMsg}</p>
        )}
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
          placeholder="Type a question…"
          className="flex-1 rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-accent"
          disabled={streaming}
        />
        <button
          type="submit"
          disabled={streaming || !draft.trim()}
          className="rounded-md bg-accent text-ink font-semibold px-4 text-sm disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </section>
  );
}
