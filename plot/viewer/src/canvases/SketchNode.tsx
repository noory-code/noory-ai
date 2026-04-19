import { memo } from "react";
import { Handle, NodeResizer, Position, type NodeProps } from "reactflow";
import { EditableText } from "../edit/EditableText";

export interface SketchNodeData {
  label: string;
  body: string;
  color: string;
  width: number;
  height: number;
  onLabelChange?: (next: string) => void;
  onOpenBody?: () => void;
  onResize?: (width: number, height: number) => void;
}

function SketchNodeComponent({ id, data, selected }: NodeProps<SketchNodeData>) {
  const ring = selected ? "ring-2 ring-indigo-500" : "ring-1 ring-slate-300";
  return (
    <>
      <NodeResizer
        minWidth={120}
        minHeight={60}
        isVisible={selected}
        lineClassName="!border-indigo-400"
        handleClassName="!h-2 !w-2 !border !border-indigo-500 !bg-white"
        onResizeEnd={(_evt, params) => {
          data.onResize?.(params.width, params.height);
        }}
      />
      <div
        className={`relative h-full w-full rounded-md bg-white px-3 py-2 shadow-sm ${ring}`}
        style={{ backgroundColor: data.color }}
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

        <div className="text-sm font-semibold text-slate-800">
          {data.onLabelChange ? (
            <EditableText
              value={data.label}
              onCommit={data.onLabelChange}
              placeholder="(untitled — click to edit)"
              ariaLabel="Node label"
            />
          ) : (
            <span>{data.label || <span className="italic text-slate-400">(untitled)</span>}</span>
          )}
        </div>
        {data.body && (
          <div className="mt-1 line-clamp-[8] whitespace-pre-wrap text-xs text-slate-700">
            {data.body}
          </div>
        )}
      </div>
    </>
  );
}

export const SketchNode = memo(SketchNodeComponent);
