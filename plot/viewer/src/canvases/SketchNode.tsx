import { memo } from "react";
import { Handle, Position, type NodeProps } from "reactflow";

export interface SketchNodeData {
  label: string;
  body: string;
  color: string;
  width: number;
  height: number;
}

/**
 * Generic node for the sketch canvas. Read-only in v0.1 commit 2 —
 * editing lands in commit 3. Handles are on all four sides so edges
 * can originate from any direction once ``nodesConnectable`` turns on.
 */
function SketchNodeComponent({ data, selected }: NodeProps<SketchNodeData>) {
  const ring = selected ? "ring-2 ring-indigo-500" : "ring-1 ring-slate-300";
  return (
    <div
      className={`relative rounded-md bg-white px-3 py-2 shadow-sm ${ring}`}
      style={{
        backgroundColor: data.color,
        width: data.width,
        minHeight: data.height,
      }}
    >
      <Handle type="target" position={Position.Top} id="t" className="!bg-slate-400" />
      <Handle type="target" position={Position.Left} id="l" className="!bg-slate-400" />
      <Handle type="source" position={Position.Right} id="r" className="!bg-slate-400" />
      <Handle type="source" position={Position.Bottom} id="b" className="!bg-slate-400" />

      <div className="text-sm font-semibold text-slate-800">
        {data.label || <span className="italic text-slate-400">(untitled)</span>}
      </div>
      {data.body && (
        <div className="mt-1 line-clamp-3 whitespace-pre-wrap text-xs text-slate-700">
          {data.body}
        </div>
      )}
    </div>
  );
}

export const SketchNode = memo(SketchNodeComponent);
