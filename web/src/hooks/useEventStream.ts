import { useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import type { AgentEvent } from "../lib/types";

export function useEventStream(onEvent: (e: AgentEvent) => void) {
  const { token } = useAuth();
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!token) return;
    let active = true;

    const connect = () => {
      // EventSource can't set headers — pass token as query param
      const url = `/api/events/stream?token=${encodeURIComponent(token)}`;
      const es = new EventSource(url);
      esRef.current = es;

      es.onmessage = (e) => {
        try {
          const payload: AgentEvent = JSON.parse(e.data);
          onEvent(payload);
        } catch {
          // ignore malformed frames
        }
      };

      es.onerror = () => {
        es.close();
        if (active) setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      active = false;
      esRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);
}
