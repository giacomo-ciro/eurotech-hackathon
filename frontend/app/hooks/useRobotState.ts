"use client";

import { useEffect, useState } from "react";
import { robotSocketUrl } from "../lib/api";
import type { RobotStateEvent } from "../lib/types";

const OFFLINE: RobotStateEvent = { stage: "offline", detail: "connecting…" };

export function useRobotState() {
  const [event, setEvent] = useState<RobotStateEvent>(OFFLINE);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let retryHandle: number | null = null;
    let cancelled = false;

    function connect() {
      socket = new WebSocket(robotSocketUrl());
      socket.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data) as RobotStateEvent;
          setEvent(data);
        } catch {
          // ignore
        }
      };
      socket.onclose = () => {
        setEvent({ stage: "offline", detail: "reconnecting…" });
        if (!cancelled) {
          retryHandle = window.setTimeout(connect, 2000);
        }
      };
      socket.onerror = () => {
        socket?.close();
      };
    }

    connect();

    return () => {
      cancelled = true;
      if (retryHandle) window.clearTimeout(retryHandle);
      socket?.close();
    };
  }, []);

  return event;
}
