/**
 * Top-level placeholder states for the App shell — loading, error,
 * "no projects yet". Extracted from ``App.tsx`` (v0.16.2).
 *
 * These are grouped in one file because each is < 15 LOC and they
 * share no internal logic; one-component-per-file would be all
 * boilerplate without modularity benefit.
 */
export function Loading() {
  return (
    <div className="flex h-full items-center justify-center text-fg-muted">
      Loading…
    </div>
  );
}

export function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center p-8 text-center">
      <div>
        <h1 className="mb-2 text-xl font-semibold text-danger-fg">
          Something broke
        </h1>
        <p className="font-mono text-xs text-fg-secondary">{message}</p>
      </div>
    </div>
  );
}

export function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="flex h-full items-center justify-center p-8 text-center">
      <div>
        <h1 className="mb-2 text-2xl font-semibold">No projects yet</h1>
        <p className="mb-6 text-fg-muted">
          Create your first Plot project to start mapping.
        </p>
        <button
          type="button"
          onClick={onCreate}
          className="rounded-md bg-surface-inverse px-4 py-2 text-sm font-medium text-fg-inverse hover:bg-surface-inverse"
        >
          Add a Project
        </button>
      </div>
    </div>
  );
}
