/**
 * v0.23.0 (D-2026-05-17-I) — Inspector section that lists a node's
 * published MD versions. Each row shows {version, published_at, sha}
 * and is a button that opens PublishedMDModal with the file contents.
 *
 * Empty state ("No published versions yet") shows for nodes that have
 * never been published.
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { listPublishedVersions, type PublishedVersion } from "../../../api";
import { PublishedMDModal } from "../../PublishedMDModal";

export interface PublishedVersionsSectionProps {
  projectPath: string;
  projectId: string;
  canvasKind: string;
  nodeId: string;
  /** Service id for service_detail canvases (mirrors publishNode arg). */
  serviceId?: string;
  /** Bumps a refresh; parent passes ``node.version`` so the list
   *  re-fetches after a publish. */
  refreshKey: string;
}

export function PublishedVersionsSection({
  projectPath,
  projectId,
  canvasKind,
  nodeId,
  serviceId,
  refreshKey,
}: PublishedVersionsSectionProps) {
  const { t } = useTranslation();
  const [versions, setVersions] = useState<PublishedVersion[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openVersion, setOpenVersion] = useState<PublishedVersion | null>(null);

  useEffect(() => {
    let cancelled = false;
    setVersions(null);
    setError(null);
    listPublishedVersions(projectPath, projectId, canvasKind, nodeId, serviceId)
      .then((vs) => {
        if (cancelled) return;
        setVersions(vs);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, [projectPath, projectId, canvasKind, nodeId, serviceId, refreshKey]);

  return (
    <section className="mt-4 border-t border-line pt-3">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-fg-muted">
        {t("inspector.publishedVersions")}
      </h3>
      {error && (
        <div className="rounded border border-danger bg-danger-soft p-2 text-[11px] text-danger-fg">
          {error}
        </div>
      )}
      {!error && versions !== null && versions.length === 0 && (
        <div className="text-[11px] text-fg-faint">
          {t("inspector.publishedVersionsEmpty")}
        </div>
      )}
      {!error && versions !== null && versions.length > 0 && (
        <ul className="space-y-1">
          {versions.map((v) => (
            <li key={v.version}>
              <button
                type="button"
                onClick={() => setOpenVersion(v)}
                className="flex w-full items-baseline justify-between rounded px-2 py-1 text-left hover:bg-surface-subtle"
              >
                <span className="font-mono text-xs font-semibold text-fg-strong">
                  {v.version}
                </span>
                <span className="ml-2 flex-1 truncate text-[11px] text-fg-muted">
                  {v.published_at ?? ""}
                </span>
                {v.sha && (
                  <span className="ml-2 font-mono text-[10px] text-fg-faint">
                    {v.sha}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
      {openVersion && (
        <PublishedMDModal
          projectPath={projectPath}
          projectId={projectId}
          version={openVersion.version}
          path={openVersion.path}
          publishedAt={openVersion.published_at}
          sha={openVersion.sha}
          onClose={() => setOpenVersion(null)}
        />
      )}
    </section>
  );
}
