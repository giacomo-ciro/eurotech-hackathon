import Link from "next/link";
import type { Session } from "../lib/types";

type Props = { session: Session };

const STATE_COLORS: Record<string, string> = {
  idle: "bg-slate-500/20 text-slate-300 border-slate-500/40",
  recording: "bg-accent/20 text-accent border-accent/50",
  captioning: "bg-warn/20 text-warn border-warn/50",
  saved: "bg-ok/20 text-ok border-ok/50",
  error: "bg-bad/20 text-bad border-bad/50",
};

export function SessionCard({ session }: Props) {
  const pill = STATE_COLORS[session.state] ?? STATE_COLORS.idle;
  return (
    <article className="rounded-xl bg-panel border border-slate-800 p-4">
      <header className="flex items-center justify-between mb-3">
        <h3 className="text-xs uppercase tracking-widest text-slate-400">Active session</h3>
        <span className={`text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full border ${pill}`}>
          {session.state}
        </span>
      </header>

      <p className="text-lg font-semibold leading-tight">{session.task}</p>
      <p className="text-sm text-slate-400 mt-1">
        {session.robot} · {session.operator}
      </p>

      <dl className="mt-3 grid grid-cols-2 gap-y-2 gap-x-3 text-sm">
        <div>
          <dt className="text-slate-500">Target dataset</dt>
          <dd>
            <Link
              href={`/datasets/${session.dataset_id}`}
              className="text-accent hover:underline"
            >
              {session.dataset_id}
            </Link>
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">Episodes saved</dt>
          <dd className="font-semibold">{session.episode_count}</dd>
        </div>
      </dl>

      <p className="mt-3 text-xs font-mono text-slate-500">{session.id}</p>
    </article>
  );
}
