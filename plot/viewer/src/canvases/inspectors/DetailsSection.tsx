/**
 * Long-form ``details.md`` section. Shared chrome for every per-kind
 * inspector — extracted from the legacy ``SketchInspector`` so the new
 * ``BaseInspector`` shell and the legacy inspector consume the same
 * implementation.
 *
 * Two states:
 *   - ``node.details_path`` set → render the MD editor for that file.
 *   - not set → render a "Create details" button that mints the folder
 *     + file then patches ``details_path`` onto the node.
 */
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { createFolder } from "../../api";
import { MDFileEditor } from "../../edit/MDFileEditor";
import { folderSlug } from "../../lib/slug";
import type { CanvasKind, SketchNode } from "../../types";

export interface DetailsSectionProps {
  node: SketchNode;
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

export function DetailsSection({
  node,
  projectPath,
  projectId,
  canvasKind,
  onPatchNode,
}: DetailsSectionProps) {
  const { t } = useTranslation();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  if (node.details_path) {
    return (
      <div className="-mx-3 mb-4 h-[50vh] border-y border-slate-200">
        <MDFileEditor
          projectPath={projectPath}
          path={node.details_path}
          projectId={projectId}
          nodeId={node.id}
          canvasKind={canvasKind}
        />
      </div>
    );
  }

  const onCreate = async () => {
    if (busy) return;
    setBusy(true);
    setErr(null);
    try {
      const canvasSlug = canvasKind;
      const desired = node.kind
        ? folderSlug(node.kind, node.label || node.kind, canvasSlug)
        : `${canvasSlug}/${node.id}`;
      const actualPath = await createFolder(projectPath, projectId, desired);
      // Server seeds an empty ``index.md``; v0.9 wants the file named
      // ``details.md`` instead. Convention: use ``${actualPath}/details.md``.
      onPatchNode({ details_path: `${actualPath}/details.md` });
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mb-4 rounded border border-dashed border-slate-300 p-2 text-xs">
      <div className="mb-1 font-semibold text-slate-600">
        {t("inspector.longFormDetailsHeader")}
      </div>
      <div className="mb-2 text-[11px] text-slate-500">
        {t("inspector.longFormDetailsIntro")}
      </div>
      <button
        type="button"
        onClick={onCreate}
        disabled={busy}
        className="rounded bg-slate-900 px-2 py-1 text-[11px] font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {busy ? t("inspector.creating") : t("inspector.createDetails")}
      </button>
      {err && <div className="mt-2 text-[11px] text-rose-600">{err}</div>}
    </div>
  );
}
