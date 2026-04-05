import { useReducer, useEffect, useRef, useCallback } from 'react';
import type { ServerMessage, HumanInputMessage } from '../types/messages';
import type { AppState } from '../store/actorState';
import { initialState, reducer } from '../store/actorState';

const WS_URL = '/ws'; // proxied by Vite dev server to ws://localhost:8000/ws

const MAX_BACKOFF_MS = 30_000;

export function useAnimaSocket(): [AppState, (content: string) => void] {
  const [state, dispatch] = useReducer(reducer, undefined, initialState);
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);
  const unmountedRef = useRef(false);

  const connect = useCallback(() => {
    if (unmountedRef.current) return;

    dispatch({ type: 'CONNECTION_STATUS', status: 'connecting' });
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      backoffRef.current = 1000;
      dispatch({ type: 'CONNECTION_STATUS', status: 'connected' });
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as ServerMessage;
        dispatch({ type: 'SERVER_MESSAGE', message });
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      if (unmountedRef.current) return;
      dispatch({ type: 'CONNECTION_STATUS', status: 'disconnected' });
      const delay = backoffRef.current;
      backoffRef.current = Math.min(delay * 2, MAX_BACKOFF_MS);
      setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    unmountedRef.current = false;  // reset on each mount (handles StrictMode double-invoke)
    connect();
    return () => {
      unmountedRef.current = true;
      wsRef.current?.close();
    };
  }, [connect]);

  const sendHumanInput = useCallback((content: string) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) return;
    const message: HumanInputMessage = { type: 'human_input', content };
    wsRef.current.send(JSON.stringify(message));
    dispatch({ type: 'HUMAN_SENT', content });
  }, []);

  return [state, sendHumanInput];
}
