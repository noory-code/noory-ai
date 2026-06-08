/**
 * EchoGuard (D-2026-06-08-A, step 3).
 *
 * When the viewer PUTs a canvas, the engine broadcasts a `project_changed`
 * event back to the *originating* client too. The socket layer must skip that
 * self-echo (otherwise it refetches + clears undo history as if an external
 * client had changed the doc). This guard tracks, per canvas key, how many of
 * our own writes are still awaiting their echo.
 *
 * It replaces the previous `Set<CanvasKey>` guard, which had two bugs:
 *  - PUT error left the key in the Set forever → every later *real* external
 *    change to that key was silently dropped (treated as our echo).
 *  - the Set is count-blind → two in-flight writes to the same key produced
 *    two echoes but only one delete, so the second echo was mishandled.
 *
 * Design: a per-key counter. `expect()` on PUT send, `consume()` on each echo
 * (true = ours, skip), `fail()` on PUT error. A TTL safety net decrements a
 * stuck entry so a never-arriving echo cannot leak. Over-decrement is the safe
 * direction — it only causes a redundant refetch, never a dropped external
 * change.
 */
export interface EchoGuard {
  /** A write was just sent for `key`; expect one server echo. */
  expect(key: string): void;
  /**
   * A `project_changed` for `key` arrived. Returns `true` if it is one of our
   * own pending echoes (caller should skip), `false` if it is external.
   */
  consume(key: string): boolean;
  /** The write failed / was abandoned; no echo will arrive for it. */
  fail(key: string): void;
  /** Pending (un-echoed) write count for `key` — for tests/diagnostics. */
  pending(key: string): number;
}

const DEFAULT_TTL_MS = 15_000;

export function createEchoGuard(opts?: { ttlMs?: number }): EchoGuard {
  const ttlMs = opts?.ttlMs ?? DEFAULT_TTL_MS;
  const counts = new Map<string, number>();

  const decrement = (key: string) => {
    const n = counts.get(key) ?? 0;
    if (n <= 1) counts.delete(key);
    else counts.set(key, n - 1);
  };

  return {
    expect(key) {
      counts.set(key, (counts.get(key) ?? 0) + 1);
      // Safety net: if the echo never comes (lost PUT, no broadcast), retire
      // the pending slot so a future external change isn't suppressed.
      setTimeout(() => decrement(key), ttlMs);
    },
    consume(key) {
      if ((counts.get(key) ?? 0) > 0) {
        decrement(key);
        return true;
      }
      return false;
    },
    fail(key) {
      decrement(key);
    },
    pending(key) {
      return counts.get(key) ?? 0;
    },
  };
}
