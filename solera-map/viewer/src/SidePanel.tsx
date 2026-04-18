import { useState } from "react";
import { patchConcept } from "./api";
import type { SelectedNode } from "./canvases/PlanCanvas";
import { MarkdownBody } from "./MarkdownBody";
import type { BranchSide, Concept, Graph, Identity, Layout } from "./types";

interface SidePanelProps {
  graph: Graph;
  selection: SelectedNode | null;
  projectPath: string;
  layout: Layout;
  onClose: () => void;
  onMutated: () => void;
  onLayoutChange: (next: Layout) => void;
}

export function SidePanel({
  graph,
  selection,
  projectPath,
  layout,
  onClose,
  onMutated,
  onLayoutChange,
}: SidePanelProps) {
  if (selection === null) return null;
  return (
    <aside className="flex w-96 flex-col border-l border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-2">
        <span className="text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          {selection.kind === "identity" ? "Identity" : "Concept"}
        </span>
        <button
          onClick={onClose}
          className="rounded px-2 py-0.5 text-sm text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          aria-label="Close panel"
        >
          ✕
        </button>
      </div>
      <div className="flex-1 overflow-auto px-4 py-3 text-sm">
        {selection.kind === "identity" && graph.identity !== null ? (
          <IdentityBody identity={graph.identity} />
        ) : (
          <ConceptBody
            graph={graph}
            conceptId={selection.id}
            projectPath={projectPath}
            layout={layout}
            onMutated={onMutated}
            onLayoutChange={onLayoutChange}
          />
        )}
      </div>
    </aside>
  );
}

function IdentityBody({ identity }: { identity: Identity }) {
  return (
    <div className="space-y-5">
      <Section title="Mission" body={identity.mission} />
      <Section title="Vision" body={identity.vision} />
      <Section title="Core Values" body={identity.values} />
      <Section title="Tone & Manner" body={identity.tone_and_manner} />
      <Section title="Goals" body={identity.goals} />
      {Object.entries(identity.extras ?? {}).map(([key, body]) => (
        <Section key={key} title={humanizeStem(key)} body={body} />
      ))}
    </div>
  );
}

function humanizeStem(stem: string): string {
  return stem
    .split(/[-_]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function ConceptBody({
  graph,
  conceptId,
  projectPath,
  layout,
  onMutated,
  onLayoutChange,
}: {
  graph: Graph;
  conceptId: string;
  projectPath: string;
  layout: Layout;
  onMutated: () => void;
  onLayoutChange: (next: Layout) => void;
}) {
  const concept = graph.concepts.find((c) => c.id === conceptId);
  if (!concept) return <EmptyState text="Concept not found." />;

  const children = graph.concepts.filter((c) => c.parent === concept.id);
  const isTopLevel = !concept.parent || !graph.concepts.some((c) => c.id === concept.parent);

  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-lg font-semibold text-ink">{concept.name}</h2>
        <div className="mt-0.5 flex items-center gap-2 text-[11px] text-slate-400">
          <span className="font-mono">{concept.id}</span>
          <StatusChip status={concept.status} />
        </div>
      </header>
      <ParentSelect
        graph={graph}
        concept={concept}
        projectPath={projectPath}
        onMutated={onMutated}
      />
      {isTopLevel && (
        <SideToggle
          conceptId={concept.id}
          layout={layout}
          onLayoutChange={onLayoutChange}
        />
      )}
      {children.length > 0 && (
        <MetaRow label="Children" value={children.map((c) => c.name).join(", ")} />
      )}
      <Section title="Intent" body={concept.intent} tone="north-star" />
      <Section title="Current Design" body={concept.current_design} tone="sketch" />
      <Section title="Current Shape" body={concept.current_shape} tone="live" />
      {concept.horizon && <Section title="Horizon" body={concept.horizon} />}
    </div>
  );
}

function SideToggle({
  conceptId,
  layout,
  onLayoutChange,
}: {
  conceptId: string;
  layout: Layout;
  onLayoutChange: (next: Layout) => void;
}) {
  const nodeKey = `concept:${conceptId}`;
  const current: BranchSide = layout.nodes[nodeKey]?.side ?? "right";

  const setSide = (next: BranchSide) => {
    if (next === current) return;
    // Drop x/y on this node AND all its descendants so the fresh bilateral
    // auto-layout can place them on the new side. Keep the `side` hint.
    const nextNodes = { ...layout.nodes };
    const prior = layout.nodes[nodeKey] ?? {};
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { x: _px, y: _py, ...rest } = prior;
    nextNodes[nodeKey] = { ...rest, side: next };
    onLayoutChange({ ...layout, nodes: nextNodes });
  };

  return (
    <div className="flex items-start gap-3 text-[12px]">
      <span className="mt-1 w-16 shrink-0 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
        Side
      </span>
      <div className="flex gap-1 rounded-md bg-slate-100 p-0.5">
        <SideButton active={current === "left"} onClick={() => setSide("left")}>
          ← Left
        </SideButton>
        <SideButton active={current === "right"} onClick={() => setSide("right")}>
          Right →
        </SideButton>
      </div>
    </div>
  );
}

function SideButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded px-2.5 py-1 text-[11px] font-medium transition ${
        active ? "bg-white text-ink shadow-sm" : "text-slate-500 hover:text-slate-800"
      }`}
    >
      {children}
    </button>
  );
}

function ParentSelect({
  graph,
  concept,
  projectPath,
  onMutated,
}: {
  graph: Graph;
  concept: Concept;
  projectPath: string;
  onMutated: () => void;
}) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Avoid listing descendants to prevent cycles on the client too.
  const descendantIds = collectDescendants(concept.id, graph.concepts);
  const options = graph.concepts.filter(
    (c) => c.id !== concept.id && !descendantIds.has(c.id),
  );

  const onChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const nextParent = value === "__none__" ? null : value;
    if (nextParent === concept.parent) return;
    setSaving(true);
    setError(null);
    try {
      await patchConcept(projectPath, concept.id, { parent: nextParent });
      onMutated();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex items-start gap-3 text-[12px]">
      <span className="mt-1 w-16 shrink-0 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
        Parent
      </span>
      <div className="flex-1">
        <select
          value={concept.parent ?? "__none__"}
          onChange={onChange}
          disabled={saving}
          className="w-full rounded border border-slate-300 bg-white px-2 py-1 text-[12px] focus:border-sketch focus:outline-none"
        >
          <option value="__none__">— (top-level surface)</option>
          {options.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        {error && <div className="mt-1 text-[11px] text-rose-500">{error}</div>}
      </div>
    </div>
  );
}

function collectDescendants(id: string, concepts: Concept[]): Set<string> {
  const out = new Set<string>();
  const visit = (parentId: string) => {
    for (const c of concepts) {
      if (c.parent === parentId && !out.has(c.id)) {
        out.add(c.id);
        visit(c.id);
      }
    }
  };
  visit(id);
  return out;
}

function Section({
  title,
  body,
  tone,
}: {
  title: string;
  body: string | null;
  tone?: "north-star" | "sketch" | "live";
}) {
  if (body === null || body.trim() === "") {
    return (
      <div>
        <SectionTitle title={title} tone={tone} />
        <p className="text-[12px] italic text-slate-400">not set</p>
      </div>
    );
  }
  return (
    <div>
      <SectionTitle title={title} tone={tone} />
      <MarkdownBody text={body} />
    </div>
  );
}

function SectionTitle({
  title,
  tone,
}: {
  title: string;
  tone?: "north-star" | "sketch" | "live";
}) {
  const toneClass =
    tone === "north-star"
      ? "text-amber-600"
      : tone === "sketch"
        ? "text-sketch"
        : tone === "live"
          ? "text-live"
          : "text-slate-500";
  return (
    <div className={`mb-1 text-[10px] font-semibold uppercase tracking-widest ${toneClass}`}>
      {title}
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-3 text-[12px]">
      <span className="w-16 shrink-0 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
        {label}
      </span>
      <span className="text-slate-700">{value}</span>
    </div>
  );
}

function StatusChip({ status }: { status: string }) {
  const color =
    status === "active"
      ? "bg-emerald-50 text-emerald-700"
      : status === "deprecated"
        ? "bg-rose-50 text-rose-700"
        : "bg-slate-100 text-slate-600";
  return (
    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${color}`}>{status}</span>
  );
}

function EmptyState({ text }: { text: string }) {
  return <p className="text-sm italic text-slate-400">{text}</p>;
}
