/**
 * v0.23.0 (D-2026-05-17-I) — Modal that fetches and renders a published
 * MD file. Reuses the SketchBodyModal scaffold (backdrop + click-outside
 * close + Escape key) and MDPreview (GFM + Mermaid + error fallback).
 */
import { useEffect, useState } from "react";

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

  return (
    <div
      className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/40"
      role="dialog"
      aria-modal="true"
      aria-label={`Published ${version}`}
      onClick={onClose}
    >
      <div
        className="flex max-h-[90vh] w-[720px] flex-col rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
          <div className="flex items-baseline gap-3">
            <span className="font-mono text-sm font-semibold text-slate-800">
              {version}
            </span>
            <span className="text-xs text-slate-500">{path}</span>
          </div>
          <div className="flex items-center gap-3">
            {publishedAt && (
              <span className="text-[11px] text-slate-500">{publishedAt}</span>
            )}
            {sha && (
              <span className="font-mono text-[11px] text-slate-400">{sha}</span>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close"
              className="rounded px-2 text-slate-400 hover:bg-slate-100"
            >
              ✕
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {error && (
            <pre className="rounded border border-rose-300 bg-rose-50 p-3 text-xs text-rose-800">
              {error}
            </pre>
          )}
          {content === null && !error && (
            <div className="text-xs text-slate-400">Loading...</div>
          )}
          {content !== null && <MDPreview content={content} />}
        </div>
      </div>
    </div>
  );
}
