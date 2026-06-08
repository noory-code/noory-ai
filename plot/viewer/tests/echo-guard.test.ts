/**
 * EchoGuard (D-2026-06-08-A, step 3). The viewer PUTs a canvas, the engine
 * broadcasts `project_changed` back to the ORIGINATING client, and the socket
 * layer must skip that self-echo (not refetch + clear undo history). The old
 * `Set<CanvasKey>` guard leaked forever on PUT error (suppressing later real
 * external changes) and mismatched on multiple in-flight writes. EchoGuard
 * replaces it with a per-key in-flight COUNT + a TTL safety net + an explicit
 * fail() for the PUT-error path.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

import { createEchoGuard } from "../src/lib/echoGuard";

afterEach(() => {
  vi.useRealTimers();
});

describe("EchoGuard", () => {
  it("consume() returns true once per expected echo, false afterward", () => {
    const g = createEchoGuard();
    g.expect("k");
    expect(g.consume("k")).toBe(true); // our own echo → skip
    expect(g.consume("k")).toBe(false); // nothing pending → external
  });

  it("matches multiple in-flight writes to the same key by count", () => {
    const g = createEchoGuard();
    g.expect("k");
    g.expect("k");
    expect(g.consume("k")).toBe(true);
    expect(g.consume("k")).toBe(true);
    expect(g.consume("k")).toBe(false); // both echoes consumed → external
  });

  it("fail() drops a pending write so a later external change is NOT suppressed", () => {
    const g = createEchoGuard();
    g.expect("k");
    g.fail("k"); // PUT errored → no echo will arrive
    expect(g.consume("k")).toBe(false); // external change must come through
  });

  it("TTL clears a stuck entry whose echo never arrived (no permanent leak)", () => {
    vi.useFakeTimers();
    const g = createEchoGuard({ ttlMs: 1000 });
    g.expect("k");
    vi.advanceTimersByTime(1001);
    expect(g.consume("k")).toBe(false); // leaked entry was cleared by TTL
  });

  it("is per-key and never goes negative", () => {
    const g = createEchoGuard();
    expect(g.consume("x")).toBe(false); // unknown key
    g.expect("a");
    expect(g.consume("b")).toBe(false); // different key untouched
    expect(g.consume("a")).toBe(true);
    expect(g.consume("a")).toBe(false);
  });
});
