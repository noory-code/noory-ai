/**
 * Effective project-path helper (v0.33.0, D-2026-05-31-M).
 *
 * A workspace root holds many projects, each in its own subdirectory
 * (`dir`, POSIX-relative to the root; `"."` for a root-level project).
 * The effective `project_path` for a project's server I/O is the root
 * joined with its dir.
 */

/** Join a workspace root with a project's relative dir.
 *  `"."` (root-level) returns the root unchanged. */
export function joinWorkspaceDir(root: string, dir: string): string {
  const trimmedDir = dir.trim();
  if (trimmedDir === "" || trimmedDir === ".") return root;
  const base = root.replace(/\/+$/, "");
  const rel = trimmedDir.replace(/^\/+/, "");
  return `${base}/${rel}`;
}
