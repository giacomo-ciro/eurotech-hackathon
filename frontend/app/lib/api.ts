import type {
  ActivePrescriptionDetail,
  ChatMessage,
  Interaction,
  Medicine,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export const RERUN_URL =
  process.env.NEXT_PUBLIC_RERUN_URL ?? "http://localhost:9090";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export function getActivePrescription(): Promise<ActivePrescriptionDetail> {
  return getJSON<ActivePrescriptionDetail>("/api/prescriptions/active");
}

export function getMedicine(drugId: number): Promise<Medicine> {
  return getJSON<Medicine>(`/api/medicines/${drugId}`);
}

export function getInteractions(drugId: number): Promise<Interaction[]> {
  return getJSON<Interaction[]>(`/api/medicines/${drugId}/interactions`);
}

export async function startDispense(prescriptionId: string): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/prescriptions/${prescriptionId}/dispense`,
    { method: "POST" },
  );
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Dispense failed: ${res.status} ${detail}`);
  }
}

export function robotSocketUrl(): string {
  const httpBase = API_BASE.replace(/\/$/, "");
  const wsBase = httpBase.replace(/^http/, "ws");
  return `${wsBase}/ws/robot`;
}

export type ChatStreamCallbacks = {
  onToken: (text: string) => void;
  onDone: () => void;
  onError: (message: string) => void;
};

export async function streamChat(
  drugId: number,
  messages: ChatMessage[],
  callbacks: ChatStreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ drug_id: drugId, messages }),
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
