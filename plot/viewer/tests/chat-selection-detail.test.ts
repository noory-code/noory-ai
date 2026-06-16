/**
 * Regression (D-2026-06-16-F): the chat's per-turn selection context (Layer 2,
 * D-2026-06-15-A) was inert on the service-detail canvas — App wired
 * ``onSelectionChange`` only on the main F/A/S ``<Canvas>`` slot, and the
 * ``ChatDock`` selection was read from ``activeCanvas`` (the Services canvas),
 * not the active detail canvas. So while editing inside a service-detail
 * canvas, "이거 고쳐줘" couldn't resolve the selected node.
 *
 * Static guard (App wiring is integration-heavy): pin that (1) the
 * ServiceDetailCanvas slot reports its selection up, and (2) the ChatDock
 * selection source is detail-aware.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const src = readFileSync(resolve(__dirname, "../src/App.tsx"), "utf8");

function jsxBlock(tag: string): string {
  const start = src.indexOf(`<${tag}`);
  if (start === -1) return "";
  const end = src.indexOf("/>", start);
  return src.slice(start, end === -1 ? undefined : end);
}

describe("chat selection on service-detail (D-2026-06-16-F)", () => {
  it("ServiceDetailCanvas reports its selection upward", () => {
    expect(jsxBlock("ServiceDetailCanvas")).toContain("onSelectionChange");
  });

  it("ChatDock selection reads the active detail canvas, not just activeCanvas", () => {
    expect(jsxBlock("ChatDock")).toContain("detailCanvas");
  });

  // D-2026-06-16-G — the chat syncs to the active PROJECT (+ canvas), not the
  // whole workspace/monorepo. ChatDock keys on the active project path.
  it("ChatDock keys the chat on the active project path (per-project sync)", () => {
    expect(jsxBlock("ChatDock")).toContain("activeProjectPath");
  });
});
