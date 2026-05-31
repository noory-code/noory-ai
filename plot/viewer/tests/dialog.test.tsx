// v0.35.0 (D-2026-05-31-W) — in-app dialog system replacing native
// window.confirm / alert / prompt. Pins the promise-based imperative API:
// confirm → boolean, prompt → string|null, alert → void; Escape / Cancel
// resolve the negative branch.

import { describe, expect, it } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { DialogProvider, useDialog } from "../src/shell/dialog/DialogProvider";

function Harness({ onResult }: { onResult: (v: unknown) => void }) {
  const dialog = useDialog();
  return (
    <div>
      <button onClick={async () => onResult(await dialog.confirm({ message: "Delete X?" }))}>
        run-confirm
      </button>
      <button
        onClick={async () => onResult(await dialog.prompt({ message: "Name?", defaultValue: "init" }))}
      >
        run-prompt
      </button>
      <button
        onClick={async () => {
          await dialog.alert({ message: "Oops" });
          onResult("alerted");
        }}
      >
        run-alert
      </button>
    </div>
  );
}

function setup() {
  const results: unknown[] = [];
  render(
    <DialogProvider>
      <Harness onResult={(v) => results.push(v)} />
    </DialogProvider>,
  );
  return results;
}

describe("DialogProvider — confirm", () => {
  it("resolves true when the accept button is clicked", async () => {
    const results = setup();
    fireEvent.click(screen.getByText("run-confirm"));
    expect(screen.getByText("Delete X?")).toBeTruthy();
    fireEvent.click(screen.getByTestId("dialog-accept"));
    await waitFor(() => expect(results).toEqual([true]));
  });

  it("resolves false when the cancel button is clicked", async () => {
    const results = setup();
    fireEvent.click(screen.getByText("run-confirm"));
    fireEvent.click(screen.getByTestId("dialog-cancel"));
    await waitFor(() => expect(results).toEqual([false]));
  });

  it("resolves false on Escape", async () => {
    const results = setup();
    fireEvent.click(screen.getByText("run-confirm"));
    fireEvent.keyDown(window, { key: "Escape" });
    await waitFor(() => expect(results).toEqual([false]));
  });
});

describe("DialogProvider — prompt", () => {
  it("resolves the typed value on accept", async () => {
    const results = setup();
    fireEvent.click(screen.getByText("run-prompt"));
    const input = screen.getByTestId("dialog-input") as HTMLInputElement;
    expect(input.value).toBe("init");
    fireEvent.change(input, { target: { value: "hello" } });
    fireEvent.click(screen.getByTestId("dialog-accept"));
    await waitFor(() => expect(results).toEqual(["hello"]));
  });

  it("resolves null on cancel", async () => {
    const results = setup();
    fireEvent.click(screen.getByText("run-prompt"));
    fireEvent.click(screen.getByTestId("dialog-cancel"));
    await waitFor(() => expect(results).toEqual([null]));
  });
});

describe("DialogProvider — alert", () => {
  it("resolves void on OK", async () => {
    const results = setup();
    fireEvent.click(screen.getByText("run-alert"));
    expect(screen.getByText("Oops")).toBeTruthy();
    fireEvent.click(screen.getByTestId("dialog-accept"));
    await waitFor(() => expect(results).toEqual(["alerted"]));
  });

  it("shows only one dialog at a time", () => {
    setup();
    fireEvent.click(screen.getByText("run-confirm"));
    expect(screen.getAllByTestId("dialog-panel")).toHaveLength(1);
  });
});
