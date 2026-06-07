/**
 * v0.23.0 (D-2026-05-17-I) — Modal that fetches and renders a published
 * MD file. Reuses the SketchBodyModal scaffold (backdrop + click-outside
 * close + Escape key) and MDPreview (GFM + Mermaid + error fallback).
 *
 * v0.23.2 (D-2026-05-17-K) — rendered via createPortal into document.body
 * so the modal centres on the **viewport**, not on the Inspector aside.
 * (The aside has `backdrop-blur` which makes it a containing block for
 * its `position: fixed` descendants, so without a portal the modal got
 * trapped inside the Inspector strip.) Modal container is resizable
 * via CSS `resize: both`.
 */
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import { readFile } from "../api";
import { MDPreview } from "../edit/MDPreview";

export interface PublishedMDModalProps {
  projectPath: string;
  projectId: string;
  version: string;
  path: string;
  publishedAt: string | null;
  sha: string | null;
  onClose: () => void;
}

export function PublishedMDModal({
  projectPath,
  projectId,
  version,
  path,
  publishedAt,
  sha,
  onClose,
}: PublishedMDModalProps) {
  const [content, setContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    readFile(projectPath, projectId, path)
      .then((md) => {
        if (cancelled) return;
        setContent(md);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, [projectPath, projectId, path]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const modal = (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/40"
      role="dialog"
      aria-modal="true"
      aria-label={`Published ${version}`}
      onClick={onClose}
    >
      <div
        className="flex flex-col overflow-hidden rounded-lg bg-surface shadow-xl"
        style={{
          width: "720px",
          height: "80vh",
          minWidth: "360px",
          minHeight: "240px",
          maxWidth: "95vw",
          maxHeight: "95vh",
          resize: "both",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-line px-5 py-3">
          <div className="flex items-baseline gap-3">
            <span className="font-mono text-sm font-semibold text-fg-strong">
              {version}
            </span>
            <span className="text-xs text-fg-muted">{path}</span>
          </div>
          <div className="flex items-center gap-3">
            {publishedAt && (
              <span className="text-[11px] text-fg-muted">{publishedAt}</span>
            )}
            {sha && (
              <span className="font-mono text-[11px] text-fg-faint">{sha}</span>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close"
              className="rounded px-2 text-fg-faint hover:bg-surface-subtle"
            >
              ✕
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {error && (
            <pre className="rounded border border-danger bg-danger-soft p-3 text-xs text-danger-fg">
              {error}
            </pre>
          )}
          {content === null && !error && (
            <div className="text-xs text-fg-faint">Loading...</div>
          )}
          {content !== null && <MDPreview content={content} />}
        </div>
      </div>
    </div>
  );
  return createPortal(modal, document.body);
}
