/**
 * R7 chat — stream subscription + message-list state (D-2026-06-12-D, Phase C).
 *
 * Opens one WS per workspace and demultiplexes ``chat_stream_event`` payloads
 * into a flat list of messages the dock can render. The user's own messages
 * are appended optimistically on ``send`` so the panel feels instant; the
 * assistant message lands on ``turn_start`` and grows with each ``delta``.
 *
 * State machine per assistant turn::
 *
 *   turn_start  → push a streaming assistant message (empty text)
 *   delta       → append to the streaming message's text
 *   turn_complete → mark complete; reconcile against ``text`` so a
 *                   late-joining subscriber that missed deltas still gets
 *                   the full transcript
 *   error       → mark the streaming message as errored, surface
 *                  ``error_message``
 */
import { useCallback, useEffect, useRef, useState } from "react";

import {
  resetChatSession as resetChatSessionApi,
  sendChatMessage as sendChatMessageApi,
} from "../app/chat";
import { openProjectSocket, type SocketStatus } from "../api";
import type { ChatStreamSocketPayload, SocketEvent } from "../types";

export type ChatMessageRole = "user" | "assistant";

export type ChatMessageStatus = "streaming" | "complete" | "error";

export interface ChatMessage {
  /** Stable id — ``turn_<turn_id>`` for assistant turns, ``user_<nonce>`` for
   *  user turns (so React keeps the row stable across streaming updates). */
  id: string;
  role: ChatMessageRole;
  text: string;
  status: ChatMessageStatus;
  /** Surfaced as inline error text when ``status === "error"``. */
  errorMessage?: string;
}

export interface UseChatStreamResult {
  messages: ChatMessage[];
  socketStatus: SocketStatus;
  isStreaming: boolean;
  send: (message: string) => Promise<void>;
  reset: () => Promise<void>;
  lastSendError: string | null;
}

export function useChatStream(
  workspaceRoot: string | null | undefined,
): UseChatStreamResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [socketStatus, setSocketStatus] =
    useState<SocketStatus>("connecting");
  const [isStreaming, setIsStreaming] = useState(false);
  const [lastSendError, setLastSendError] = useState<string | null>(null);

  // Tracks which turn id is currently streaming so we always update the
  // right assistant row even if the user submits a new turn before the
  // previous one closes (rare but possible — the engine queues).
  const streamingTurnRef = useRef<string | null>(null);

  useEffect(() => {
    if (!workspaceRoot) return;
    streamingTurnRef.current = null;
    setSocketStatus("connecting");
    const handle = openProjectSocket(workspaceRoot, {
      onStatus: setSocketStatus,
      onEvent: (event: SocketEvent) => {
        if (event.event !== "chat_stream_event") return;
        applyChatEvent(event as SocketEvent & ChatStreamSocketPayload, {
          setMessages,
          streamingTurnRef,
          setIsStreaming,
        });
      },
      onError: (err) => setLastSendError(err),
    });
    return () => handle.close();
  }, [workspaceRoot]);

  const send = useCallback(
    async (message: string) => {
      if (!workspaceRoot) return;
      const trimmed = message.trim();
      if (!trimmed) return;
      setLastSendError(null);
      const userId = `user_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      setMessages((prev) => [
        ...prev,
        { id: userId, role: "user", text: trimmed, status: "complete" },
      ]);
      setIsStreaming(true);
      try {
        await sendChatMessageApi(workspaceRoot, trimmed);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setLastSendError(msg);
        setIsStreaming(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === userId ? { ...m, status: "error", errorMessage: msg } : m,
          ),
        );
      }
    },
    [workspaceRoot],
  );

  const reset = useCallback(async () => {
    if (!workspaceRoot) return;
    try {
      await resetChatSessionApi(workspaceRoot);
      setMessages([]);
      streamingTurnRef.current = null;
      setIsStreaming(false);
      setLastSendError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setLastSendError(msg);
    }
  }, [workspaceRoot]);

  return { messages, socketStatus, isStreaming, send, reset, lastSendError };
}

// ---------------------------------------------------------------------------
// Pure reducer over a single chat_stream_event — extracted so the hook stays
// declarative and the test suite can drive the state machine without React.
// ---------------------------------------------------------------------------

interface _ApplyArgs {
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  streamingTurnRef: React.MutableRefObject<string | null>;
  setIsStreaming: React.Dispatch<React.SetStateAction<boolean>>;
}

function applyChatEvent(
  event: ChatStreamSocketPayload,
  { setMessages, streamingTurnRef, setIsStreaming }: _ApplyArgs,
): void {
  const assistantId = `turn_${event.turn_id}`;
  switch (event.type) {
    case "turn_start": {
      streamingTurnRef.current = event.turn_id;
      setIsStreaming(true);
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: "assistant",
          text: "",
          status: "streaming",
        },
      ]);
      return;
    }
    case "delta": {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, text: m.text + (event.text ?? "") }
            : m,
        ),
      );
      return;
    }
    case "turn_complete": {
      streamingTurnRef.current = null;
      setIsStreaming(false);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                // Reconcile against the engine's accumulated text when it
                // arrives — protects late subscribers from missing deltas.
                text: event.text || m.text,
                status: "complete",
              }
            : m,
        ),
      );
      return;
    }
    case "error": {
      streamingTurnRef.current = null;
      setIsStreaming(false);
      setMessages((prev) => {
        // If the error landed before turn_start (rare but possible —
        // provider crashed instantly), append a fresh error row instead of
        // silently dropping the event.
        const existing = prev.find((m) => m.id === assistantId);
        if (!existing) {
          return [
            ...prev,
            {
              id: assistantId,
              role: "assistant",
              text: "",
              status: "error",
              errorMessage: event.error_message ?? "unknown error",
            },
          ];
        }
        return prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                status: "error",
                errorMessage: event.error_message ?? "unknown error",
              }
            : m,
        );
      });
      return;
    }
  }
}

// Exported for tests.
export const _applyChatEventForTest = applyChatEvent;
