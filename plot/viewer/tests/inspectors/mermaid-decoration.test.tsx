/**
 * v0.21.0 Live Preview Stage 2 (D-2026-05-17-D) — mermaid SVG inline
 * decoration tests.
 *
 * The decoration must:
 *   1. NOT mutate the markdown source (SSOT invariant).
 *   2. Render mermaid SVG output below a ``` ```mermaid``` `` fence
 *      after the debounce window elapses.
 *   3. Swap in a labelled error block when mermaid.render rejects.
 *
 * ``mermaidLoader`` is mocked so vitest never pulls the real mermaid
 * package into the test bundle (and tests stay deterministic across
 * mermaid library upgrades).
 */
import "@testing-library/jest-dom/vitest";
import { render, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const mockRender = vi.fn();
vi.mock("../../src/edit/mermaidLoader", () => ({
  loadMermaid: vi.fn(() =>
    Promise.resolve({
      render: mockRender,
    }),
  ),
}));

import { MdTextarea } from "../../src/canvases/inspectors/shared/MdTextarea";

const MERMAID_SOURCE = ["```mermaid", "flowchart LR", "  A --> B", "```"].join("\n");

// 200 ms debounce + render microtasks; 400 ms is comfortably past it.
const RENDER_TIMEOUT = 1500;

beforeEach(() => {
  mockRender.mockReset();
  mockRender.mockImplementation((_id: string, _code: string) =>
    Promise.resolve({ svg: '<svg data-test="mermaid-svg"><g/></svg>' }),
  );
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("mermaid decoration — SSOT invariant", () => {
  it("does not mutate the markdown source when a mermaid block is rendered", async () => {
    const handleChange = vi.fn();
    const { container } = render(
      <MdTextarea value={MERMAID_SOURCE} onChange={handleChange} />,
    );

    // Wait until the mocked render has been dispatched at least once;
    // that's the signal the decoration pipeline has run end-to-end.
    await waitFor(
      () => {
        expect(mockRender).toHaveBeenCalled();
      },
      { timeout: RENDER_TIMEOUT },
    );

    // The read-only mirror reflects the prop value verbatim.
    const mirror = container.querySelector("textarea[aria-hidden]");
    expect(mirror).toHaveValue(MERMAID_SOURCE);

    // The decoration must never round-trip through onChange.
    expect(handleChange).not.toHaveBeenCalled();
  });
});

describe("mermaid decoration — happy path", () => {
  it("renders the mermaid SVG widget after the debounce window", async () => {
    const { container } = render(
      <MdTextarea value={MERMAID_SOURCE} onChange={vi.fn()} />,
    );

    await waitFor(
      () => {
        const svg = container.querySelector('svg[data-test="mermaid-svg"]');
        expect(svg).not.toBeNull();
      },
      { timeout: RENDER_TIMEOUT },
    );

    expect(mockRender).toHaveBeenCalledTimes(1);
    const [, code] = mockRender.mock.calls[0]!;
    // CodeMirror's CodeText node may or may not include the trailing
    // newline depending on the markdown parser version; assert on the
    // diagram-defining content instead.
    expect(code).toContain("flowchart LR");
    expect(code).toContain("A --> B");
  });
});

describe("mermaid decoration — error path", () => {
  it("renders a labelled error block when mermaid.render rejects", async () => {
    mockRender.mockReset();
    mockRender.mockImplementation(() => Promise.reject(new Error("bad syntax")));

    const { container } = render(
      <MdTextarea value={MERMAID_SOURCE} onChange={vi.fn()} />,
    );

    await waitFor(
      () => {
        const err = container.querySelector('[data-mermaid="error"]');
        expect(err).not.toBeNull();
      },
      { timeout: RENDER_TIMEOUT },
    );

    const err = container.querySelector('[data-mermaid="error"]');
    expect(err?.textContent).toContain("bad syntax");
  });
});
