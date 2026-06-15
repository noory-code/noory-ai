/**
 * Chat activity indicator (D-2026-06-16-B) — makes a streaming turn feel
 * alive (bouncing dots + elapsed seconds) instead of frozen.
 */
import "@testing-library/jest-dom/vitest";
import { render, renderHook, screen, act } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  ChatActivityIndicator,
  useElapsedSeconds,
} from "../src/shell/ChatActivityIndicator";
import "../src/i18n";

afterEach(() => {
  vi.useRealTimers();
});

describe("ChatActivityIndicator (D-2026-06-16-B)", () => {
  it("renders a polite status with the working label and an elapsed counter", () => {
    render(<ChatActivityIndicator />);
    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-label", "Working…");
    expect(status).toHaveAttribute("aria-live", "polite");
    expect(status.textContent).toContain("0s"); // starts at 0
  });

  it("renders three animated dots", () => {
    const { container } = render(<ChatActivityIndicator />);
    const dots = container.querySelectorAll("span.animate-bounce");
    expect(dots).toHaveLength(3);
  });
});

describe("useElapsedSeconds", () => {
  it("counts up once per second while active", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useElapsedSeconds(true));
    expect(result.current).toBe(0);
    act(() => {
      vi.advanceTimersByTime(3000);
    });
    expect(result.current).toBe(3);
  });

  it("resets to 0 when it goes inactive", () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(
      ({ active }) => useElapsedSeconds(active),
      { initialProps: { active: true } },
    );
    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(result.current).toBe(5);
    rerender({ active: false });
    expect(result.current).toBe(0);
  });
});
