/**
 * Pointer-based stencil drag (D-2026-06-13-C). WKWebView (the bundled
 * Tauri `.app` — Plot's only product surface now) does not fire HTML5
 * `dragstart` / `drop`, so the old `draggable` + `dataTransfer` stencil
 * drop created no node on any canvas. This replaces it with a
 * pointerdown → window-pointerup channel that works in WKWebView and
 * Chromium alike. These tests pin the channel contract:
 *   - a drag begun on a stencil item, released over a registered pane,
 *     calls that pane's `place(preset, clientX, clientY)`;
 *   - a release OUTSIDE any registered pane places nothing;
 *   - when two panes are registered (main canvas + feature modal),
 *     the pane that actually contains the release point gets it.
 */
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { useRef } from "react";
import { describe, expect, it, vi } from "vitest";
import {
  StencilDragProvider,
  useStencilDrag,
  useStencilDropTarget,
} from "../src/canvases/sketch/StencilDragContext";
import type { StencilPreset } from "../src/canvases/SketchStencil";

const PRESET: StencilPreset = {
  id: "category",
  kind: "category",
  shape: "rectangle",
  color: "#e2e8f0",
  labelHint: "Category",
};

function DragSource() {
  const { beginDrag } = useStencilDrag();
  return (
    <button type="button" onPointerDown={(e) => beginDrag(PRESET, e)}>
      drag-me
    </button>
  );
}

function DropPane({ label, place }: { label: string; place: (p: StencilPreset, x: number, y: number) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  useStencilDropTarget(ref, place);
  return (
    <div ref={ref} data-testid={label} style={{ width: 100, height: 100 }}>
      {label}
    </div>
  );
}

describe("StencilDragContext — pointer drag channel", () => {
  it("places on the pane the pointer is released over", () => {
    const place = vi.fn();
    render(
      <StencilDragProvider>
        <DragSource />
        <DropPane label="pane" place={place} />
      </StencilDragProvider>,
    );
    fireEvent.pointerDown(screen.getByText("drag-me"));
    fireEvent.pointerUp(screen.getByTestId("pane"), { clientX: 42, clientY: 24 });
    expect(place).toHaveBeenCalledTimes(1);
    expect(place).toHaveBeenCalledWith(PRESET, 42, 24);
  });

  it("places nothing when released outside any registered pane", () => {
    const place = vi.fn();
    render(
      <StencilDragProvider>
        <DragSource />
        <DropPane label="pane" place={place} />
        <div data-testid="outside">outside</div>
      </StencilDragProvider>,
    );
    fireEvent.pointerDown(screen.getByText("drag-me"));
    fireEvent.pointerUp(screen.getByTestId("outside"), { clientX: 1, clientY: 1 });
    expect(place).not.toHaveBeenCalled();
  });

  it("routes via elementFromPoint when the pointer is captured to the source (WebKit)", () => {
    const place = vi.fn();
    render(
      <StencilDragProvider>
        <DragSource />
        <DropPane label="pane" place={place} />
      </StencilDragProvider>,
    );
    const paneEl = screen.getByTestId("pane");
    // jsdom has no elementFromPoint; define a stub that returns the pane
    // (what WebKit would return under the captured pointer).
    const orig = (document as { elementFromPoint?: unknown }).elementFromPoint;
    (document as unknown as { elementFromPoint: () => Element }).elementFromPoint =
      () => paneEl;
    fireEvent.pointerDown(screen.getByText("drag-me"));
    // Implicit capture: the release event's target is the SOURCE item, not
    // the pane. elementFromPoint must be what resolves the drop.
    fireEvent.pointerUp(screen.getByText("drag-me"), { clientX: 50, clientY: 50 });
    expect(place).toHaveBeenCalledWith(PRESET, 50, 50);
    (document as { elementFromPoint?: unknown }).elementFromPoint = orig;
  });

  it("pointercancel aborts the drag — a later release places nothing", () => {
    const place = vi.fn();
    render(
      <StencilDragProvider>
        <DragSource />
        <DropPane label="pane" place={place} />
      </StencilDragProvider>,
    );
    fireEvent.pointerDown(screen.getByText("drag-me"));
    fireEvent.pointerCancel(window);
    fireEvent.pointerUp(screen.getByTestId("pane"), { clientX: 5, clientY: 5 });
    expect(place).not.toHaveBeenCalled();
  });

  it("routes to the pane containing the release point (modal over main)", () => {
    const main = vi.fn();
    const modal = vi.fn();
    render(
      <StencilDragProvider>
        <DragSource />
        <DropPane label="main" place={main} />
        <DropPane label="modal" place={modal} />
      </StencilDragProvider>,
    );
    fireEvent.pointerDown(screen.getByText("drag-me"));
    fireEvent.pointerUp(screen.getByTestId("modal"), { clientX: 5, clientY: 5 });
    expect(modal).toHaveBeenCalledTimes(1);
    expect(main).not.toHaveBeenCalled();
  });
});
