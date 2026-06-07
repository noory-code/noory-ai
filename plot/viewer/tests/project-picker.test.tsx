// D-2026-06-07-A — step3 project selection UI: native folder pick in Tauri,
// URL-param hint in browser dev.

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { open as tauriOpen } from "@tauri-apps/plugin-dialog";
import { ProjectPicker } from "../src/shell/ProjectPicker";

vi.mock("@tauri-apps/plugin-dialog", () => ({ open: vi.fn() }));
vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (k: string) => k }) }));

type W = Window & { __TAURI_INTERNALS__?: unknown };

type LocationStub = { href: string };
let loc: LocationStub;

describe("ProjectPicker", () => {
  beforeEach(() => {
    loc = { href: "http://localhost/" };
    Object.defineProperty(window, "location", { value: loc, writable: true, configurable: true });
    delete (window as W).__TAURI_INTERNALS__;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows URL hint outside Tauri", () => {
    render(<ProjectPicker />);
    expect(screen.getByText("shell.projectPicker.hint")).toBeTruthy();
    expect(screen.queryByTestId("open-folder-btn")).toBeNull();
  });

  it("shows open-folder button inside Tauri", () => {
    (window as W).__TAURI_INTERNALS__ = {};
    render(<ProjectPicker />);
    expect(screen.getByTestId("open-folder-btn")).toBeTruthy();
    expect(screen.queryByText("shell.projectPicker.hint")).toBeNull();
  });

  it("calls open({ directory: true, multiple: false }) on click", async () => {
    (window as W).__TAURI_INTERNALS__ = {};
    vi.mocked(tauriOpen).mockResolvedValue("/Users/test/project");
    render(<ProjectPicker />);
    fireEvent.click(screen.getByTestId("open-folder-btn"));
    await waitFor(() =>
      expect(tauriOpen).toHaveBeenCalledWith({ directory: true, multiple: false }),
    );
  });

  it("navigates to /?project_path=<selected> on successful pick", async () => {
    (window as W).__TAURI_INTERNALS__ = {};
    vi.mocked(tauriOpen).mockResolvedValue("/Users/test/my project");
    render(<ProjectPicker />);
    fireEvent.click(screen.getByTestId("open-folder-btn"));
    await waitFor(() =>
      expect(loc.href).toBe(`/?project_path=${encodeURIComponent("/Users/test/my project")}`),
    );
  });

  it("does not navigate when dialog is cancelled", async () => {
    (window as W).__TAURI_INTERNALS__ = {};
    vi.mocked(tauriOpen).mockResolvedValue(null);
    render(<ProjectPicker />);
    fireEvent.click(screen.getByTestId("open-folder-btn"));
    await waitFor(() => expect(tauriOpen).toHaveBeenCalled());
    expect(loc.href).toBe("http://localhost/");
  });
});
