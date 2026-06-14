/**
 * R7 chat — per-scope stream routing tests (D-2026-06-13-H).
 *
 * Pins ``useChatStream``'s scope behaviour: conversations are partitioned
 * per canvas scope, an incoming ``chat_stream_event`` lands in the bucket
 * named by its own ``scope`` (not the active one), switching the active
 * scope swaps which thread is shown, and ``send`` / ``reset`` carry the
 * active scope to the engine.
 */
import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { SocketEvent } from "../src/types";

const sendSpy = vi.fn(async () => {});
const resetSpy = vi.fn(async () => {});

vi.mock("../src/app/chat", () => ({
  sendChatMessage: (...args: unknown[]) => sendSpy(...args),
  resetChatSession: (...args: unknown[]) => resetSpy(...args),
}));

// Capture the WS event sink so the test can push frames synchronously.
let emit: ((event: SocketEvent) => void) | null = null;
vi.mock("../src/api", () => ({
  openProjectSocket: (
    _path: string,
    handlers: { onEvent: (e: SocketEvent) => void },
  ) => {
    emit = handlers.onEvent;
    return { close: () => {} };
  },
}));

import { useChatStream } from "../src/hooks/useChatStream";

function turn(scope: string, text: string): SocketEvent[] {
  return [
    { event: "chat_stream_event", type: "turn_start", turn_id: `${scope}-1`, text: "", error_message: null, scope } as unknown as SocketEvent,
    { event: "chat_stream_event", type: "turn_complete", turn_id: `${scope}-1`, text, error_message: null, scope } as unknown as SocketEvent,
  ];
}

beforeEach(() => {
  sendSpy.mockClear();
  resetSpy.mockClear();
  emit = null;
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("useChatStream scope routing (D-2026-06-13-H)", () => {
  it("routes an event to the bucket named by its own scope", () => {
    const { result, rerender } = renderHook(
      ({ scope }) => useChatStream("/ws", scope),
      { initialProps: { scope: "foundation" as const } },
    );

    act(() => {
      turn("actors", "actors answer").forEach((e) => emit!(e));
    });

    // Active scope is foundation → an actors-scoped turn must not show here.
    expect(result.current.messages).toHaveLength(0);

    // Switching to actors reveals the actors thread.
    rerender({ scope: "actors" as const } as never);
    expect(result.current.messages.map((m) => m.text)).toEqual([
      "actors answer",
    ]);
  });

  it("keeps separate threads per scope across switches", () => {
    const { result, rerender } = renderHook(
      ({ scope }) => useChatStream("/ws", scope),
      { initialProps: { scope: "foundation" as const } },
    );

    act(() => {
      turn("foundation", "F answer").forEach((e) => emit!(e));
      turn("actors", "A answer").forEach((e) => emit!(e));
    });

    expect(result.current.messages.map((m) => m.text)).toEqual(["F answer"]);
    rerender({ scope: "actors" as const } as never);
    expect(result.current.messages.map((m) => m.text)).toEqual(["A answer"]);
    rerender({ scope: "foundation" as const } as never);
    expect(result.current.messages.map((m) => m.text)).toEqual(["F answer"]);
  });

  it("send carries the active scope to the engine", async () => {
    const { result } = renderHook(() => useChatStream("/ws", "services"));
    await act(async () => {
      await result.current.send("hello");
    });
    expect(sendSpy).toHaveBeenCalledWith("/ws", "hello", "services");
  });

  it("reset carries the active scope to the engine and clears only it", async () => {
    const { result, rerender } = renderHook(
      ({ scope }) => useChatStream("/ws", scope),
      { initialProps: { scope: "foundation" as const } },
    );
    act(() => {
      turn("foundation", "F answer").forEach((e) => emit!(e));
      turn("actors", "A answer").forEach((e) => emit!(e));
    });
    await act(async () => {
      await result.current.reset();
    });
    expect(resetSpy).toHaveBeenCalledWith("/ws", "foundation");
    expect(result.current.messages).toHaveLength(0); // foundation cleared
    rerender({ scope: "actors" as const } as never);
    expect(result.current.messages.map((m) => m.text)).toEqual(["A answer"]); // survived
  });
});
