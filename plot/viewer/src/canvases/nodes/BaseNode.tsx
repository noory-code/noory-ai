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
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import { Handle, Position, type NodeProps } from "reactflow";
import type { Shape } from "../../types";
import { effectiveShape } from "../sketch/nodeShape";
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

// v0.29.3 (D-2026-05-31-B) — shape now encodes producer-vs-reference:
// 원본/master kinds render a rounded rectangle (soft corners), `*_ref`
// symbol pointers render circle, `decision` renders diamond. The
// kind→shape policy lives in the pure ``nodeShape`` module so it stays
// unit-testable. Supersedes the v0.27.11 (D-2026-05-28-D) "all Symbol
// kinds are circles" rule.

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
 *  top-left is inside the visible silhouette. The check runs against
 *  the *rendered* shape (``effectiveShape``), so master kinds (now
 *  rectangles, D-2026-05-31-B) show the tag while `*_ref` circles and
 *  the `decision` diamond don't. */
export function shouldShowKindTag(shape: Shape, kind?: string | null): boolean {
  // Derive from the *rendered* shape: the corner tag shows only where
  // the silhouette has a visible top-left corner. Master kinds (now
  // rounded rectangles) get the tag; `*_ref` (circles) and `decision`
  // (diamond) don't. (D-2026-05-31-B)
  return SHAPES_WITH_VISIBLE_CORNER.has(effectiveShape(kind, shape));
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
    ? "border-2 border-accent"
    : isAnchor
      ? "border-2 border-line-strong"
      : "border border-line-strong";
  const renderShape = effectiveShape(data.kind, data.shape);
  const style = {
    backgroundColor: data.color,
    ...shapeStyle(renderShape),
  };
  const Icon = getIcon(data.icon);
  const bodyPreview = data.body;
  // v0.38.0 (D-2026-06-01-B) — nodes always auto-fit their content. The
  // manual NodeResizer is gone (user: "수동 리사이즈 없애요. 항상 자동핏").
  // Non-anchor nodes size to content (min/max width, wrap, auto height);
  // RF measures the DOM and the dimensions-change → doc plumbing persists
  // the real size for layout/edges. The synthetic anchor keeps the fixed
  // size it is given (resized via onAnchorChange), so it stays geometric.
  // v0.38.0 (D-2026-06-01-B) — round shapes (circle/ellipse incl. the
  // project anchor) auto-fit as a SQUARE (aspect-square) so they stay
  // circular; rectangular kinds fit their content width. The anchor is no
  // longer special-cased — it shrinks to its content like everything else
  // (user: "바나스 앵커는 왜 안줄이죠?").
  const isRound = renderShape === "circle" || renderShape === "ellipse";
  const sizing = isRound
    ? "w-fit aspect-square min-w-[96px] max-w-[200px]"
    : "w-fit min-w-[140px] max-w-[340px]";

  // v0.38.0 (D-2026-06-01-B) — persist the auto-fit size back to the doc so
  // RF's nodeInternals (which floating edges + auto-layout read) and the
  // saved blueprint all match the visual. Without this the node renders at
  // content size but nodeInternals keeps the stale provided width, so edges
  // attach to a phantom box ("작아지고 난 후에 연결선이 이상해졌어요"). The
  // synthetic anchor is fixed (resized via onAnchorChange) — skip it.
  const nodeRef = useRef<HTMLDivElement | null>(null);
  const reportResize = data.onResize;
  useEffect(() => {
    if (!reportResize) return;
    const el = nodeRef.current;
    if (!el) return;
    const report = () => {
      const w = Math.round(el.offsetWidth);
      const h = Math.round(el.offsetHeight);
      if (w > 0 && h > 0 && (Math.abs(w - data.width) > 1 || Math.abs(h - data.height) > 1)) {
        reportResize(w, h);
      }
    };
    report();
    const ro = new ResizeObserver(report);
    ro.observe(el);
    return () => ro.disconnect();
  }, [reportResize, data.width, data.height]);

  return (
    <>
      <div
        ref={nodeRef}
        className={`relative ${sizing} bg-surface shadow-sm ${ring} ${contentPadding(
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
        {/* v0.34.4 (D-2026-05-31-R) — all four sides are ``source`` handles
            so a connection can be started from ANY side identically;
            ConnectionMode.Loose lets them receive too. Floating edges
            ignore handle ids for rendering, and edgeTransform / handleConnect
            force the arrow toward the anchor — so which side you grab no
            longer changes the resulting edge direction. */}
        <Handle type="source" position={Position.Top} id="t" className="!bg-fg-faint" />
        <Handle type="source" position={Position.Left} id="l" className="!bg-fg-faint" />
        <Handle type="source" position={Position.Right} id="r" className="!bg-fg-faint" />
        <Handle type="source" position={Position.Bottom} id="b" className="!bg-fg-faint" />

        {showKindTag && data.kind && (
          <span className="pointer-events-none absolute left-2 top-1 text-[9px] font-semibold uppercase tracking-wider text-fg-faint">
            {t(`kindTag.${data.kind}`)}
          </span>
        )}

        {data.mdWarnings && data.mdWarnings.length > 0 && (
          <span
            className="pointer-events-none absolute right-1 top-1 rounded-full bg-surface px-1.5 py-px text-[11px] font-bold leading-tight text-warn-fg shadow-sm ring-1 ring-warn"
            title={`${data.mdWarnings.length} MD warning(s) — open Inspector for details`}
            aria-label={`${data.mdWarnings.length} markdown parse warnings`}
          >
            ⚠
          </span>
        )}

        <div
          className={`flex w-full flex-col items-stretch justify-center gap-1 ${
            isRound ? "h-full" : ""
          } ${showKindTag && !isAnchor ? "pt-3" : ""}`}
        >
          <div
            className={`flex items-center gap-1.5 text-sm font-semibold text-fg-strong ${
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
                className="nodrag flex shrink-0 items-center justify-center px-1 text-xl leading-none text-fg-muted hover:text-fg-strong"
                title={data.collapsed ? "Expand" : "Collapse"}
                aria-label={data.collapsed ? "Expand container" : "Collapse container"}
              >
                {data.collapsed ? "▸" : "▾"}
              </button>
            )}
            {Icon && <Icon size={14} className="shrink-0 text-fg-secondary" aria-hidden />}
            {data.onLabelChange ? (
              <EditableText
                value={data.label}
                onCommit={data.onLabelChange}
                placeholder="(untitled — click to edit)"
                ariaLabel="Node label"
              />
            ) : (
              <span>
                {data.label || <span className="italic text-fg-faint">(untitled)</span>}
              </span>
            )}
            {data.collapsed && data.hasChildren && (
              <span
                className="ml-auto rounded-full bg-line px-1.5 text-[10px] text-fg-secondary"
                aria-label={`${data.childCount} collapsed children`}
              >
                {data.childCount}
              </span>
            )}
          </div>
          {bodyOverride ??
            (bodyPreview && (
              <div className="nowheel overflow-auto text-left text-[11px] leading-snug text-fg [&_a]:text-accent [&_a]:underline [&_code]:rounded [&_code]:bg-surface-subtle [&_code]:px-1 [&_li]:ml-4 [&_li]:list-disc [&_p]:mb-1 [&_strong]:text-fg-strong">
                <ReactMarkdown>{bodyPreview}</ReactMarkdown>
              </div>
            ))}
        </div>
      </div>
    </>
  );
}
