/**
 * Resizable workspace layout (D-2026-06-14-E).
 *
 * Three horizontally-resizable panels — **chat (leftmost) | project sidebar |
 * canvas** — replacing the old fixed-width row + each panel's own
 * collapse/expand toggle (the user preferred free resizing over collapse).
 * Widths persist across reloads via ``useDefaultLayout`` (localStorage). Chat
 * and sidebar are collapsible (drag to the edge / double-click the separator);
 * the canvas keeps a hard minimum so it can never be squeezed away.
 *
 * Each child fills its panel (``h-full``); the panel owns the width.
 */
import type { ReactNode } from "react";
import { Group, Panel, Separator, useDefaultLayout } from "react-resizable-panels";

export interface WorkspacePanelsProps {
  chat: ReactNode;
  sidebar: ReactNode;
  canvas: ReactNode;
}

const SEPARATOR_CLASS =
  "w-1 shrink-0 cursor-col-resize bg-line transition-colors hover:bg-accent";

export function WorkspacePanels({
  chat,
  sidebar,
  canvas,
}: WorkspacePanelsProps) {
  const layout = useDefaultLayout({
    id: "plot:workspaceLayout",
    panelIds: ["chat", "sidebar", "canvas"],
    storage: localStorage,
  });
  return (
    <Group orientation="horizontal" className="flex-1" {...layout}>
      <Panel id="chat" defaultSize={22} minSize={14} collapsible>
        {chat}
      </Panel>
      <Separator className={SEPARATOR_CLASS} />
      <Panel id="sidebar" defaultSize={16} minSize={10} collapsible>
        {sidebar}
      </Panel>
      <Separator className={SEPARATOR_CLASS} />
      <Panel id="canvas" defaultSize={62} minSize={30}>
        {canvas}
      </Panel>
    </Group>
  );
}
