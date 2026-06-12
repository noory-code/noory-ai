/**
 * R7 chat — message-list reducer tests (D-2026-06-12-D, Phase C).
 *
 * Pins the pure ``applyChatEvent`` reducer that ``useChatStream`` runs for
 * every ``chat_stream_event`` payload. The hook itself is exercised via the
 * ChatDock integration tests; this file isolates the state machine so
 * regressions show up in plain JS, not via a brittle act() / WebSocket dance.
 */
import { describe, expect, it, vi } from "vitest";
import {
  _applyChatEventForTest as applyChatEvent,
  type ChatMessage,
} from "../src/hooks/useChatStream";
import type { ChatStreamSocketPayload } from "../src/types";

function buildHarness(initial: ChatMessage[] = []) {
  let messages: ChatMessage[] = [...initial];
  let isStreaming = false;
  const ref = { current: null as string | null };

  return {
    apply(event: ChatStreamSocketPayload) {
      applyChatEvent(event, {
        // The reducer pushes a callback into setMessages; jam it through
        // synchronously so the test stays sync.
        setMessages: ((updater: unknown) => {
          messages =
            typeof updater === "function"
              ? (updater as (prev: ChatMessage[]) => ChatMessage[])(messages)
              : (updater as ChatMessage[]);
        }) as React.Dispatch<React.SetStateAction<ChatMessage[]>>,
        streamingTurnRef: ref,
        setIsStreaming: ((updater: unknown) => {
          isStreaming =
            typeof updater === "function"
              ? (updater as (prev: boolean) => boolean)(isStreaming)
              : (updater as boolean);
        }) as React.Dispatch<React.SetStateAction<boolean>>,
      });
    },
    get messages() {
      return messages;
    },
    get isStreaming() {
      return isStreaming;
    },
    get streamingTurnId() {
      return ref.current;
    },
  };
}

describe("applyChatEvent (D-2026-06-12-D)", () => {
  it("turn_start appends a streaming assistant row + flips isStreaming", () => {
    const h = buildHarness();
    h.apply({
      event: "chat_stream_event",
      type: "turn_start",
      turn_id: "t1",
      text: "",
      error_message: null,
    } as ChatStreamSocketPayload);

    expect(h.messages).toHaveLength(1);
    expect(h.messages[0]).toMatchObject({
      id: "turn_t1",
      role: "assistant",
      status: "streaming",
      text: "",
    });
    expect(h.isStreaming).toBe(true);
    expect(h.streamingTurnId).toBe("t1");
  });

  it("delta appends text to the matching turn row only", () => {
    const h = buildHarness();
    h.apply({ type: "turn_start", turn_id: "t1", text: "", error_message: null } as ChatStreamSocketPayload);
    h.apply({ type: "delta", turn_id: "t1", text: "Hello ", error_message: null } as ChatStreamSocketPayload);
    h.apply({ type: "delta", turn_id: "t1", text: "world.", error_message: null } as ChatStreamSocketPayload);

    expect(h.messages[0].text).toBe("Hello world.");
    expect(h.messages[0].status).toBe("streaming");
  });

  it("turn_complete reconciles full text against the streaming row", () => {
    const h = buildHarness();
    h.apply({ type: "turn_start", turn_id: "t1", text: "", error_message: null } as ChatStreamSocketPayload);
    h.apply({ type: "delta", turn_id: "t1", text: "partial", error_message: null } as ChatStreamSocketPayload);
    // The engine emits the accumulated text on turn_complete; if it differs
    // from what we saw via deltas (late subscriber), the engine value wins.
    h.apply({
      type: "turn_complete",
      turn_id: "t1",
      text: "partial and full",
      error_message: null,
    } as ChatStreamSocketPayload);

    expect(h.messages[0].text).toBe("partial and full");
    expect(h.messages[0].status).toBe("complete");
    expect(h.isStreaming).toBe(false);
    expect(h.streamingTurnId).toBeNull();
  });

  it("turn_complete without engine text preserves the streamed text", () => {
    const h = buildHarness();
    h.apply({ type: "turn_start", turn_id: "t1", text: "", error_message: null } as ChatStreamSocketPayload);
    h.apply({ type: "delta", turn_id: "t1", text: "all good", error_message: null } as ChatStreamSocketPayload);
    h.apply({ type: "turn_complete", turn_id: "t1", text: "", error_message: null } as ChatStreamSocketPayload);

    expect(h.messages[0].text).toBe("all good");
    expect(h.messages[0].status).toBe("complete");
  });

  it("error marks the streaming row as errored + surfaces the message", () => {
    const h = buildHarness();
    h.apply({ type: "turn_start", turn_id: "t1", text: "", error_message: null } as ChatStreamSocketPayload);
    h.apply({
      type: "error",
      turn_id: "t1",
      text: "",
      error_message: "claude exited 2",
    } as ChatStreamSocketPayload);

    expect(h.messages[0].status).toBe("error");
    expect(h.messages[0].errorMessage).toBe("claude exited 2");
    expect(h.isStreaming).toBe(false);
  });

  it("error without a prior turn_start still surfaces an error row", () => {
    const h = buildHarness();
    h.apply({
      type: "error",
      turn_id: "t1",
      text: "",
      error_message: "engine offline",
    } as ChatStreamSocketPayload);

    expect(h.messages).toHaveLength(1);
    expect(h.messages[0]).toMatchObject({
      id: "turn_t1",
      role: "assistant",
      status: "error",
      errorMessage: "engine offline",
    });
  });

  it("late delta for an unknown turn id is dropped silently", () => {
    const h = buildHarness();
    h.apply({ type: "turn_start", turn_id: "t1", text: "", error_message: null } as ChatStreamSocketPayload);
    h.apply({ type: "delta", turn_id: "t2", text: "stray", error_message: null } as ChatStreamSocketPayload);
    expect(h.messages[0].text).toBe(""); // unchanged
  });
});

// Defensive — make sure vi is referenced somewhere so unused-import lint stays quiet.
const _vi = vi;
void _vi;
