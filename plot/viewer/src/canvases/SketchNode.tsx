import { memo } from "react";
import { Handle, NodeResizer, Position, type NodeProps } from "reactflow";
import type { Shape } from "../types";
import { EditableText } from "../edit/EditableText";
import { getIcon } from "./SketchIcons";

export interface SketchNodeData {
  label: string;
  body: string;
  color: string;
  width: number;
  height: number;
  shape: Shape;
  icon: string | null;
  onLabelChange?: (next: string) => void;
  onOpenBody?: () => void;
  onResize?: (width: number, height: number) => void;
  /** v0.2: set when this node contains children. Enables the fold button. */
  hasChildren?: boolean;
  /** v0.2: current fold state. */
  collapsed?: boolean;
  /** v0.2: callback to flip fold state. */
  onToggleCollapse?: () => void;
  /** v0.2: count of nested children (shown on the fold badge when collapsed). */
  childCount?: number;
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
  const centred = data.shape === "circle" || data.shape === "ellipse" || data.shape === "diamond";
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
          data.onOpenBody?.();
        }}
      >
        <Handle type="target" position={Position.Top} id="t" className="!bg-slate-400" />
        <Handle type="target" position={Position.Left} id="l" className="!bg-slate-400" />
        <Handle type="source" position={Position.Right} id="r" className="!bg-slate-400" />
        <Handle type="source" position={Position.Bottom} id="b" className="!bg-slate-400" />

        <div
          className={`flex h-full w-full flex-col gap-1 ${
            centred ? "items-center justify-center text-center" : ""
          }`}
        >
          <div className="flex items-center gap-1.5 text-sm font-semibold text-slate-800">
            {data.hasChildren && data.onToggleCollapse && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  data.onToggleCollapse?.();
                }}
                className="nodrag flex h-4 w-4 shrink-0 items-center justify-center rounded text-[10px] text-slate-600 hover:bg-slate-200"
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
          {data.body && (
            <div
              className={`line-clamp-[8] whitespace-pre-wrap text-xs text-slate-700 ${
                centred ? "text-center" : ""
              }`}
            >
              {data.body}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export const SketchNode = memo(SketchNodeComponent);
