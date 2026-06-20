/**
 * CanvasTabs shows the active project NAME centered in the tab bar
 * (v0.34.3, D-2026-05-31-Q). The workspace root path lives in the header.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "../src/i18n";
import { describe, expect, it, vi } from "vitest";
import { CanvasTabs } from "../src/shell/CanvasTabs";

describe("CanvasTabs project name (D-2026-05-31-Q)", () => {
  it("renders the active project name centered", () => {
    render(
      <CanvasTabs
        active="foundation"
        onSelect={vi.fn()}
        blueprintVersion="v0.1.0"
        onPublishBlueprint={vi.fn()}
        projectName="Banas"
      />,
    );
    expect(screen.getByText("Banas")).toBeInTheDocument();
  });
});

describe("CanvasTabs — dynamic service-detail tab (D-2026-06-15-H)", () => {
  it("appends the {ServiceDetail} tab (by service name) and closes it", async () => {
    const user = userEvent.setup();
    const onSelectDetail = vi.fn();
    const onCloseDetail = vi.fn();
    render(
      <CanvasTabs
        active="services"
        onSelect={vi.fn()}
        blueprintVersion="v0.1.0"
        onPublishBlueprint={vi.fn()}
        projectName="Banas"
        detailServiceId="svc_1"
        detailLabel="Login service"
        detailActive
        onSelectDetail={onSelectDetail}
        onCloseDetail={onCloseDetail}
      />,
    );
    const detailTab = screen.getByRole("tab", { name: "Login service" });
    expect(detailTab.getAttribute("aria-selected")).toBe("true");
    // While the detail tab is active, the F/A/S tabs are deselected.
    expect(
      screen.getByRole("tab", { name: /services/i }).getAttribute("aria-selected"),
    ).toBe("false");
    await user.click(screen.getByRole("button", { name: /close feature-detail/i }));
    expect(onCloseDetail).toHaveBeenCalled();
  });

  it("renders no detail tab when none is open", () => {
    render(
      <CanvasTabs
        active="services"
        onSelect={vi.fn()}
        blueprintVersion="v0.1.0"
        onPublishBlueprint={vi.fn()}
        projectName="Banas"
      />,
    );
    expect(screen.queryByRole("button", { name: /close feature-detail/i })).toBeNull();
  });
});
