import { memo } from "react";
import ReactMarkdown from "react-markdown";
import { Handle, NodeResizer, Position, type NodeProps } from "reactflow";
import type { Shape } from "../types";
import { EditableText } from "../edit/EditableText";
import { getIcon } from "./SketchIcons";

/**
 * Kinds the top-left tag recognises. Actors / services are identified
 * clearly enough by their icon + colour, so we only label the Core-canvas
 * kinds where the palette collapsed down to a single star+colour.
 */
const KIND_TAG_LABELS: Record<string, string> = {
  project: "PROJECT",
  mission: "MISSION",
  core_value: "CORE VALUE",
  identity: "IDENTITY",
  // v0.10 Step 5: composition kinds visible on Service-Detail canvases.
  metric: "METRIC",
  step: "STEP",
  // v0.12: category groups services on the Services canvas.
  category: "CATEGORY",
};

/** Shapes whose top-left corner is inside the visible silhouette. */
const KIND_TAG_SHAPES = new Set<Shape>(["rectangle", "rounded"]);

export interface SketchNodeData {
  label: string;
  body: string;
  color: string;
  width: number;
  height: number;
  shape: Shape;
  icon: string | null;
  /** v0.5: surfaced as the top-left "MISSION" / "CORE VALUE" / … tag so the
   * kind is legible without opening the Inspector. ``null`` / ``undefined``
   * hides the tag. */
  kind?: string | null;
  onLabelChange?: (next: string) => void;
  onOpenBody?: () => void;
  /** v0.12.1: when set, double-click invokes drill instead of opening the
   * generic edit-node modal. Wired by SketchCanvas for kinds where drill is
   * the intended dblclick gesture (services-canvas service → modal,
   * service_detail actor_ref → jump to actor master). */
  onDrill?: () => void;
  onResize?: (width: number, height: number) => void;
  /** v0.2: set when this node contains children. Enables the fold button. */
  hasChildren?: boolean;
  /** v0.2: current fold state. */
  collapsed?: boolean;
  /** v0.2: callback to flip fold state. */
  onToggleCollapse?: () => void;
  /** v0.2: count of nested children (shown on the fold badge when collapsed). */
  childCount?: number;
  /** v0.13 Phase 7: server-side MD parse warnings for this Foundation node.
   * When non-empty, the node renders a yellow ⚠ badge in its top-right;
   * the Inspector lists each warning with a link to the source file. */
  mdWarnings?: string[];
  /** v0.5: suppress the fold button even when ``onToggleCollapse`` is wired
   * (Core canvas uses peer layout; fold has no meaning there). */
  showFold?: boolean;
}

/**
 * Shape styles map to CSS. Diamond / hexagon use SVG clip-path since
 * plain border-radius can't express non-rectangular outlines.
 */
function shapeStyle(shape: Shape): React.CSSProperties {
  switch (shape) {
    case "rectangle":
      return { borderRadius: 0 };
    case "rounded":
      return { borderRadius: 8 };
    case "circle":
      return { borderRadius: "50%" };
    case "ellipse":
      return { borderRadius: "50%" };
    case "diamond":
      return { clipPath: "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)" };
    case "hexagon":
      return {
        clipPath:
          "polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)",
      };
    case "octagon":
      return {
        clipPath:
          "polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)",
      };
  }
}

/**
 * Some shapes (diamond, hexagon, circle) crop content at the edges; the
 * label/body needs interior padding to stay visible.
 */
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

function SketchNodeComponent({ id, data, selected }: NodeProps<SketchNodeData>) {
  const ring = selected
    ? "outline outline-2 outline-indigo-500"
    : "outline outline-1 outline-slate-300";
  const style = {
    backgroundColor: data.color,
    ...shapeStyle(data.shape),
  };
  const Icon = getIcon(data.icon);
  // v0.9: ``data.body`` is already the chosen typed-field preview (pulled
  // by SketchCanvas — Mission's tagline / others' summary). No parsing.
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
          data.shape,
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

        {/* Top-left kind tag. Skipped for circle/ellipse/diamond shapes where
            the corner lands outside the visible silhouette. */}
        {data.kind &&
          KIND_TAG_SHAPES.has(data.shape) &&
          KIND_TAG_LABELS[data.kind] && (
            <span className="pointer-events-none absolute left-2 top-1 text-[9px] font-semibold uppercase tracking-wider text-slate-400">
              {KIND_TAG_LABELS[data.kind]}
            </span>
          )}

        {/* v0.13 Phase 7 — yellow ⚠ badge when the node's MD template parsed
            with warnings. Inspector shows the full list; this is the at-a-
            glance signal so the user notices broken external edits. */}
        {data.mdWarnings && data.mdWarnings.length > 0 && (
          <span
            className="pointer-events-none absolute right-1 top-1 rounded-full bg-amber-100 px-1.5 text-[11px] leading-tight text-amber-800 ring-1 ring-amber-300"
            title={`${data.mdWarnings.length} MD warning(s) — open Inspector for details`}
            aria-label={`${data.mdWarnings.length} markdown parse warnings`}
          >
            ⚠
          </span>
        )}

        <div className="flex h-full w-full flex-col items-stretch justify-center gap-1">
          {/* v0.12.4: category labels align left (they read as group
              headers); other kinds — including service — stay centered. */}
          <div
            className={`flex items-center gap-1.5 text-sm font-semibold text-slate-800 ${
              data.kind === "category" ? "justify-start" : "justify-center"
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
          {bodyPreview && (
            <div className="nowheel overflow-auto text-left text-[11px] leading-snug text-slate-700 [&_a]:text-indigo-600 [&_a]:underline [&_code]:rounded [&_code]:bg-slate-100 [&_code]:px-1 [&_li]:ml-4 [&_li]:list-disc [&_p]:mb-1 [&_strong]:text-slate-900">
              <ReactMarkdown>{bodyPreview}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export const SketchNode = memo(SketchNodeComponent);
