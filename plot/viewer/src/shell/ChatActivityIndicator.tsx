/**
 * Chat activity indicator (D-2026-06-16-B).
 *
 * Makes a streaming turn feel alive instead of frozen: three bouncing dots
 * (CSS animation) + an elapsed-seconds counter. Shown in the status bar for
 * the whole streaming duration (including the gap between send and the first
 * token, while the CLI is spawning / thinking) and inside an assistant
 * bubble that has no text yet.
 *
 * User ask (2026-06-16): "채팅 과정이 좀 더 다이나믹하게 — 사람들이 기다리지만
 * 멈추지 않은 것처럼 보여야 해요."
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

/** Seconds since ``active`` last became true; 0 while inactive. */
export function useElapsedSeconds(active: boolean): number {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!active) {
      setSeconds(0);
      return;
    }
    setSeconds(0);
    // Runtime-only app code, so Date.now() is fine (mirrors useChatStream).
    const started = Date.now();
    const id = setInterval(() => {
      setSeconds(Math.floor((Date.now() - started) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [active]);
  return seconds;
}

export interface ChatActivityIndicatorProps {
  /** When false the indicator stops counting (kept for callers that mount it
   *  unconditionally). Defaults to true — most callers mount it only while a
   *  turn is streaming and unmount it when done. */
  active?: boolean;
}

export function ChatActivityIndicator({ active = true }: ChatActivityIndicatorProps) {
  const { t } = useTranslation();
  const seconds = useElapsedSeconds(active);
  return (
    <span
      role="status"
      aria-live="polite"
      aria-label={t("chat.working")}
      className="inline-flex items-center gap-1.5 text-fg-muted"
    >
      <span aria-hidden className="inline-flex items-end gap-0.5">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1 w-1 animate-bounce rounded-full bg-fg-muted"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </span>
      <span className="tabular-nums">{t("chat.elapsedSeconds", { seconds })}</span>
    </span>
  );
}
