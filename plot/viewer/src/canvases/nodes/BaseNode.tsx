/**
 * Shared chrome for every per-kind React Flow node renderer.
 *
 * v0.15 Phase 3.1 — replaces the 245-LOC ``SketchNode.tsx`` god
 * renderer that branched on ``data.kind`` for every cosmetic choice.
 * BaseNode owns: NodeResizer, the outer shape-styled div, the 4
 * Handles, the MD-warnings badge, and the label / body area.
 *
 * Per-kind renderers under ``nodes/{kind}/`` wrap BaseNode and pass
 * kind-specific overrides (currently small — kind tag membership +
 * project-anchor border — but the per-file structure is the hook
 * point for future per-kind visual variations).
 */
import { type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import { Handle, NodeResizer, Position, type NodeProps } from "reactflow";
import type { Shape } from "../../types";
import { EditableText } from "../../edit/EditableText";
import { getIcon } from "../SketchIcons";

export interface BaseNodeData {
  label: string;
  body: string;
  color: string;
  width: number;
  height: number;
  shape: Shape;
  icon: string | null;
  /** Discriminator — passed through unmodified for downstream use
   *  (i18n key for the kind tag, etc.). */
  kind?: string | null;
  onLabelChange?: (next: string) => void;
  onOpenBody?: () => void;
  onDrill?: () => void;
  onResize?: (width: number, height: number) => void;
  hasChildren?: boolean;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  childCount?: number;
  mdWarnings?: string[];
  showFold?: boolean;
  /** v0.27.19 (D-2026-05-30-A) — ServiceDetail step authoring. The
   *  step's ``outcome`` (system-side end state) rendered on-canvas +
   *  inline-editable. Only StepNode reads these; other kinds leave
   *  them undefined. */
  outcome?: string;
  onOutcomeChange?: (next: string) => void;
  /** v0.27.19 (D-2026-05-30-B) — count of outgoing directed edges.
   *  ≥ 2 marks a branch point (SPEC §"Service composition model"). */
  branchCount?: number;
}

export interface BaseNodeChromeProps {
  /** Whether to render the top-left "MISSION" / "CORE VALUE" / …
   *  kind tag. Per-kind renderers decide based on shape + identity.
   *  Default false; ``rectangle`` / ``rounded`` shapes typically
   *  set this true. */
  showKindTag?: boolean;
  /** Whether this node is a project anchor — gets the thicker
   *  slate-600 border instead of the default slate-300. */
  isAnchor?: boolean;
  /** Whether the label aligns left (category) instead of center. */
  labelAlignLeft?: boolean;
  /** Optional per-kind body override (rare; most kinds use the
   *  default markdown body preview). */
  bodyOverride?: ReactNode;
}

const SHAPES_WITH_VISIBLE_CORNER = new Set<Shape>(["rectangle", "rounded"]);

// v0.27.11 (D-2026-05-28-D) — Symbol kinds always render as circles
// regardless of ``data.shape``. Per D-2026-05-19-D, Symbol nodes are the
// cross-canvas referenceable masters (mission / core_value / identity /
// actor) plus their refs in the consumer plane; user 2026-05-28
// confirmed they should always read as circles. Force at the renderer
// layer so legacy data (mission saved as ``rounded`` pre-v0.27.11)
// snaps to circle without any data migration. ``project`` (synthetic
// anchor) is intentionally excluded — its shape is a user toggle.
const SYMBOL_KINDS = new Set<string>([
  "mission",
  "core_value",
  "identity",
  "actor",
  "actor_ref",
  "mission_ref",
  "value_ref",
  "identity_ref",
]);

function effectiveShape(data: BaseNodeData): Shape {
  if (data.kind && SYMBOL_KINDS.has(data.kind)) return "circle";
  return data.shape;
}

function shapeStyle(shape: Shape): React.CSSProperties {
  switch (shape) {
    case "rectangle":
      return { borderRadius: 0 };
    case "rounded":
      return { borderRadius: 8 };
    case "circle":
    case "ellipse":
      return { borderRadius: "50%" };
    case "diamond":
      return { clipPath: "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)" };
    case "hexagon":
      return {
        clipPath: "polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)",
      };
    case "octagon":
      return {
        clipPath:
          "polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)",
      };
  }
}

function contentPadding(shape: Shape): string {
  switch (shape) {
    case "circle":
    case "ellipse":
      return "px-6 py-4";
    case "diamond":
      return "px-8 py-6";
    case "hexagon":
    case "octagon":
      return "px-6 py-3";
    default:
      return "px-3 py-2";
  }
}

/** Convenience: per-kind renderers compose with this for the
 *  KIND_TAG_SHAPES check — the corner only renders on shapes whose
 *  top-left is inside the visible silhouette. v0.27.11
 *  (D-2026-05-28-D): when ``kind`` is a Symbol the renderer forces
 *  circle, so the corner is never visible — the kind tag has no
 *  place to render and is suppressed at this layer regardless of
 *  the stored ``shape``. */
export function shouldShowKindTag(shape: Shape, kind?: string | null): boolean {
  if (kind && SYMBOL_KINDS.has(kind)) return false;
  return SHAPES_WITH_VISIBLE_CORNER.has(shape);
}

export function BaseNode({
  id,
  data,
  selected,
  chrome = {},
}: NodeProps<BaseNodeData> & { chrome?: BaseNodeChromeProps }) {
  const { t } = useTranslation();
  const { showKindTag, isAnchor, labelAlignLeft, bodyOverride } = chrome;
  const ring = selected
    ? "border-2 border-indigo-500"
    : isAnchor
      ? "border-2 border-slate-600"
      : "border border-slate-300";
  const renderShape = effectiveShape(data);
  const style = {
    backgroundColor: data.color,
    ...shapeStyle(renderShape),
  };
  const Icon = getIcon(data.icon);
  const bodyPreview = data.body;
  return (
    <>
      <NodeResizer
        minWidth={80}
        minHeight={60}
        isVisible={selected}
        lineClassName="!border-indigo-400"
        handleClassName="!h-2 !w-2 !border !border-indigo-500 !bg-white"
        onResizeEnd={(_evt, params) => {
          data.onResize?.(params.width, params.height);
        }}
      />
      <div
        className={`relative h-full w-full bg-white shadow-sm ${ring} ${contentPadding(
          renderShape,
        )}`}
        style={style}
        data-node-id={id}
        onDoubleClick={(e) => {
          e.stopPropagation();
          if (data.onDrill) {
            data.onDrill();
          } else {
            data.onOpenBody?.();
          }
        }}
      >
        <Handle type="target" position={Position.Top} id="t" className="!bg-slate-400" />
        <Handle type="target" position={Position.Left} id="l" className="!bg-slate-400" />
        <Handle type="source" position={Position.Right} id="r" className="!bg-slate-400" />
        <Handle type="source" position={Position.Bottom} id="b" className="!bg-slate-400" />

        {showKindTag && data.kind && (
          <span className="pointer-events-none absolute left-2 top-1 text-[9px] font-semibold uppercase tracking-wider text-slate-400">
            {t(`kindTag.${data.kind}`)}
          </span>
        )}

        {data.mdWarnings && data.mdWarnings.length > 0 && (
          <span
            className="pointer-events-none absolute right-1 top-1 rounded-full bg-white px-1.5 py-px text-[11px] font-bold leading-tight text-amber-700 shadow-sm ring-1 ring-amber-500"
            title={`${data.mdWarnings.length} MD warning(s) — open Inspector for details`}
            aria-label={`${data.mdWarnings.length} markdown parse warnings`}
          >
            ⚠
          </span>
        )}

        <div className="flex h-full w-full flex-col items-stretch justify-center gap-1">
          <div
            className={`flex items-center gap-1.5 text-sm font-semibold text-slate-800 ${
              labelAlignLeft ? "justify-start" : "justify-center"
            }`}
          >
            {data.showFold !== false && data.hasChildren && data.onToggleCollapse && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  data.onToggleCollapse?.();
                }}
                className="nodrag flex shrink-0 items-center justify-center px-1 text-xl leading-none text-slate-500 hover:text-slate-900"
                title={data.collapsed ? "Expand" : "Collapse"}
                aria-label={data.collapsed ? "Expand container" : "Collapse container"}
              >
                {data.collapsed ? "▸" : "▾"}
              </button>
            )}
            {Icon && <Icon size={14} className="shrink-0 text-slate-600" aria-hidden />}
            {data.onLabelChange ? (
              <EditableText
                value={data.label}
                onCommit={data.onLabelChange}
                placeholder="(untitled — click to edit)"
                ariaLabel="Node label"
              />
            ) : (
              <span>
                {data.label || <span className="italic text-slate-400">(untitled)</span>}
              </span>
            )}
            {data.collapsed && data.hasChildren && (
              <span
                className="ml-auto rounded-full bg-slate-200 px-1.5 text-[10px] text-slate-600"
                aria-label={`${data.childCount} collapsed children`}
              >
                {data.childCount}
              </span>
            )}
          </div>
          {bodyOverride ??
            (bodyPreview && (
              <div className="nowheel overflow-auto text-left text-[11px] leading-snug text-slate-700 [&_a]:text-indigo-600 [&_a]:underline [&_code]:rounded [&_code]:bg-slate-100 [&_code]:px-1 [&_li]:ml-4 [&_li]:list-disc [&_p]:mb-1 [&_strong]:text-slate-900">
                <ReactMarkdown>{bodyPreview}</ReactMarkdown>
              </div>
            ))}
        </div>
      </div>
    </>
  );
}
