/**
 * DirTreePickerModal — drill-down + pick a target dir (D-2026-05-31-N).
 */
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../src/api";
import i18n from "../src/i18n";
import { DirTreePickerModal } from "../src/shell/DirTreePickerModal";

vi.mock("../src/api");

const promptMock = vi.fn();
vi.mock("../src/shell/dialog/DialogProvider", () => ({
  useDialog: () => ({ prompt: promptMock, confirm: vi.fn(), alert: vi.fn() }),
}));

const TREE = {
  root: {
    name: "repo",
    rel: ".",
    has_plot: false,
    children: [
      { name: "a", rel: "a", has_plot: true, children: [] },
      {
        name: "b",
        rel: "b",
        has_plot: false,
        children: [{ name: "c", rel: "b/c", has_plot: false, children: [] }],
      },
    ],
  },
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.getDirTree).mockResolvedValue(TREE as never);
});

function row(name: string): HTMLElement {
  // the row <div> containing this dir's label
  const label = screen.getByText(name);
  return label.parentElement as HTMLElement;
}

describe("DirTreePickerModal (D-2026-05-31-N)", () => {
  it("loads the tree and marks a dir that already has a project", async () => {
    render(
      <DirTreePickerModal open workspaceRoot="/repo" onClose={vi.fn()} onPick={vi.fn()} />,
    );
    await waitFor(() => expect(screen.getByText(i18n.t("dirPicker.root"))).toBeInTheDocument());
    // "a" has a project → badge + "Open" action (not "Create here")
    const a = row("a");
    expect(within(a).getByText(i18n.t("dirPicker.hasProject"))).toBeInTheDocument();
    expect(within(a).getByText(i18n.t("dirPicker.open"))).toBeInTheDocument();
  });

  it("picks the chosen dir, including a nested one after expanding", async () => {
    const onPick = vi.fn();
    render(
      <DirTreePickerModal open workspaceRoot="/repo" onClose={vi.fn()} onPick={onPick} />,
    );
    await waitFor(() => expect(screen.getByText("a")).toBeInTheDocument());

    fireEvent.click(within(row("a")).getByText(i18n.t("dirPicker.open")));
    expect(onPick).toHaveBeenCalledWith("a");

    // "b" is collapsed → expand to reveal "c"
    expect(screen.queryByText("c")).not.toBeInTheDocument();
    fireEvent.click(within(row("b")).getByRole("button", { name: "expand" }));
    fireEvent.click(within(row("c")).getByText(i18n.t("dirPicker.createHere")));
    expect(onPick).toHaveBeenCalledWith("b/c");
  });

  it("creates a NEW folder under a dir and picks it (D-2026-05-31-AC)", async () => {
    promptMock.mockResolvedValue("banana");
    vi.mocked(api.createWorkspaceDir).mockResolvedValue({ rel: "b/banana" });
    const onPick = vi.fn();
    render(
      <DirTreePickerModal open workspaceRoot="/repo" onClose={vi.fn()} onPick={onPick} />,
    );
    await waitFor(() => expect(screen.getByText("b")).toBeInTheDocument());

    fireEvent.click(within(row("b")).getByText(i18n.t("dirPicker.newFolder")));
    await waitFor(() =>
      expect(api.createWorkspaceDir).toHaveBeenCalledWith("/repo", "b/banana"),
    );
    await waitFor(() => expect(onPick).toHaveBeenCalledWith("b/banana"));
  });

  it("creates a new folder at the workspace root (rel = bare name)", async () => {
    promptMock.mockResolvedValue("banas");
    vi.mocked(api.createWorkspaceDir).mockResolvedValue({ rel: "banas" });
    const onPick = vi.fn();
    render(
      <DirTreePickerModal open workspaceRoot="/repo" onClose={vi.fn()} onPick={onPick} />,
    );
    await waitFor(() => expect(screen.getByText(i18n.t("dirPicker.root"))).toBeInTheDocument());

    fireEvent.click(within(row(i18n.t("dirPicker.root"))).getByText(i18n.t("dirPicker.newFolder")));
    await waitFor(() => expect(api.createWorkspaceDir).toHaveBeenCalledWith("/repo", "banas"));
    await waitFor(() => expect(onPick).toHaveBeenCalledWith("banas"));
  });

  it("does not create a folder when the name prompt is cancelled", async () => {
    promptMock.mockResolvedValue(null);
    const onPick = vi.fn();
    render(
      <DirTreePickerModal open workspaceRoot="/repo" onClose={vi.fn()} onPick={onPick} />,
    );
    await waitFor(() => expect(screen.getByText("b")).toBeInTheDocument());

    fireEvent.click(within(row("b")).getByText(i18n.t("dirPicker.newFolder")));
    await waitFor(() => expect(promptMock).toHaveBeenCalled());
    expect(api.createWorkspaceDir).not.toHaveBeenCalled();
    expect(onPick).not.toHaveBeenCalled();
  });
});
