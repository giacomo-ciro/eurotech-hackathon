import type {
  ChatMessage,
  Dataset,
  DatasetDetail,
  Episode,
  LeRobotEpisodeData,
  LeRobotEpisodeSummary,
  LeRobotInfo,
  Session,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export const RERUN_URL =
  process.env.NEXT_PUBLIC_RERUN_URL ?? "http://localhost:9090";

export function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export function getActiveSession(): Promise<Session> {
  return getJSON<Session>("/api/sessions/active");
}

export async function startRecording(sessionId: string): Promise<Session> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/start`, { method: "POST" });
  if (!res.ok) throw new Error(`Start failed: ${res.status} ${await res.text()}`);
  return res.json() as Promise<Session>;
}

export async function stopRecording(sessionId: string): Promise<Session> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/stop`, { method: "POST" });
  if (!res.ok) throw new Error(`Stop failed: ${res.status} ${await res.text()}`);
  return res.json() as Promise<Session>;
}

export function getDatasets(): Promise<Dataset[]> {
  return getJSON<Dataset[]>("/api/datasets");
}

export function getDataset(id: string): Promise<DatasetDetail> {
  return getJSON<DatasetDetail>(`/api/datasets/${id}`);
}

export function getEpisode(datasetId: string, episodeId: string): Promise<Episode> {
  return getJSON<Episode>(`/api/datasets/${datasetId}/episodes/${episodeId}`);
}

export function episodeRrdUrl(datasetId: string, episodeId: string): string {
  return `${API_BASE}/api/datasets/${datasetId}/episodes/${episodeId}/trajectory.rrd`;
}

export function datasetCoverUrl(id: string): string {
  return `${API_BASE}/api/datasets/${id}/cover`;
}

export function captionStreamUrl(sessionId: string): string {
  return `${API_BASE}/api/sessions/${sessionId}/captions/stream`;
}

export function getLeRobotInfo(): Promise<LeRobotInfo> {
  return getJSON<LeRobotInfo>("/api/lerobot/info");
}

export function getLeRobotEpisodes(): Promise<LeRobotEpisodeSummary[]> {
  return getJSON<LeRobotEpisodeSummary[]>("/api/lerobot/episodes");
}

export function getLeRobotEpisode(episodeIndex: number): Promise<LeRobotEpisodeData> {
  return getJSON<LeRobotEpisodeData>(`/api/lerobot/episodes/${episodeIndex}`);
}

export function lerobotVideoUrl(episodeIndex: number): string {
  return `${API_BASE}/api/lerobot/episodes/${episodeIndex}/video`;
}

export function robotSocketUrl(): string {
  const wsBase = API_BASE.replace(/^http/, "ws").replace(/\/$/, "");
  return `${wsBase}/ws/robot`;
}

export type ChatContext = {
  session_id?: string;
  dataset_id?: string;
  episode_id?: string;
};

export type ChatStreamCallbacks = {
  onToken: (text: string) => void;
  onDone: () => void;
  onError: (message: string) => void;
};

export async function streamChat(
  messages: ChatMessage[],
  context: ChatContext,
  callbacks: ChatStreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, ...context }),
    signal,
  });
  if (!res.ok || !res.body) {
    callbacks.onError(`Chat failed: ${res.status} ${res.statusText}`);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const raw of events) {
      const lines = raw.split("\n");
      let eventName = "message";
      let dataLine = "";
      for (const line of lines) {
        if (line.startsWith("event:")) eventName = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLine += line.slice(5).trim();
      }
      if (!dataLine) continue;
      try {
        const data = JSON.parse(dataLine);
        if (eventName === "token") callbacks.onToken(data.text ?? "");
        else if (eventName === "done") callbacks.onDone();
        else if (eventName === "error") callbacks.onError(data.message ?? "unknown error");
      } catch {
        // ignore malformed line
      }
    }
  }
}
