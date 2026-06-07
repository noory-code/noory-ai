/**
 * ProjectPicker i18n binding — regression for the step3 (D-2026-06-07-A/B)
 * namespace bug.
 *
 * The bug: ProjectPicker called ``useTranslation("shell")`` and looked up
 * keys WITHOUT the ``shell.`` prefix (``t("projectPicker.title")`` etc.).
 * This project loads a single ``translation`` namespace (see
 * ``src/i18n/index.ts`` ``resources: { en: { translation: en } }``) per the
 * convention pinned in D-2026-05-11-D — there is no ``shell`` namespace, so
 * every key resolved to its raw string ("projectPicker.title" was shown
 * verbatim in the app).
 *
 * Why the sibling ``project-picker.test.tsx`` did NOT catch it: that file
 * mocks ``react-i18next`` with ``t: (k) => k``, which returns the key
 * regardless of namespace — so a namespace bug is invisible there.
 *
 * This file uses the REAL i18n bundle (no react-i18next mock) and asserts
 * the rendered text is the translated value, never the raw key.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import i18n from "../src/i18n";
import { ProjectPicker } from "../src/shell/ProjectPicker";

// ProjectPicker imports ``open`` from the Tauri dialog plugin at module
// load; stub it so the import resolves under JSDOM.
vi.mock("@tauri-apps/plugin-dialog", () => ({ open: vi.fn() }));

type W = Window & { __TAURI_INTERNALS__?: unknown };

describe("ProjectPicker i18n (real bundle)", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("en");
    delete (window as W).__TAURI_INTERNALS__;
  });

  it("renders the translated title, not the raw key", () => {
    render(<ProjectPicker />);
    const title = i18n.t("shell.projectPicker.title");
    expect(title).not.toBe("shell.projectPicker.title"); // sanity: key resolves
    expect(screen.getByText(title)).toBeInTheDocument();
    expect(screen.queryByText("projectPicker.title")).toBeNull();
  });

  it("renders the translated URL hint outside Tauri, not the raw key", () => {
    render(<ProjectPicker />);
    const hint = i18n.t("shell.projectPicker.hint");
    expect(hint).not.toBe("shell.projectPicker.hint"); // sanity: key resolves
    expect(screen.getByText(hint)).toBeInTheDocument();
    expect(screen.queryByText("projectPicker.hint")).toBeNull();
  });

  it("renders the translated open-folder label inside Tauri, not the raw key", () => {
    (window as W).__TAURI_INTERNALS__ = {};
    render(<ProjectPicker />);
    const label = i18n.t("shell.projectPicker.openFolder");
    expect(label).not.toBe("shell.projectPicker.openFolder"); // sanity: key resolves
    expect(screen.getByText(label)).toBeInTheDocument();
    expect(screen.queryByText("projectPicker.openFolder")).toBeNull();
  });
});
