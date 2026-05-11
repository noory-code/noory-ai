import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { createFolder } from "../api";
import { MDFileEditor } from "../edit/MDFileEditor";
import { folderSlug } from "../lib/slug";
import type { CanvasKind, SketchNode } from "../types";

export interface SketchInspectorProps {
  /** Currently selected node. Null → panel shows empty state. */
  node: SketchNode | null;
  /** All nodes so we can find composition children of a Service. */
  allNodes: SketchNode[];
  /**
   * v0.2 multi-canvas: actors across all canvases. Lets the Inspector
   * detect orphan ``actor_ref`` nodes without false positives caused by
   * the per-tab filtered view.
   */
  availableActors: SketchNode[];
  /** v0.10 Step 3: foundation masters so the Inspector can render
   *  ref-target labels for the three foundation ref kinds. */
  availableMissions?: SketchNode[];
  availableValues?: SketchNode[];
  availableIdentities?: SketchNode[];
  /** Patch the selected node's own fields. */
  onPatchNode: (patch: Partial<SketchNode>) => void;
  /** Create a new rule/content child under ``parentId``. */
  onAddChild: (parentId: string, kind: "rule" | "content") => void;
  /** Patch an existing child. */
  onPatchChild: (childId: string, patch: Partial<SketchNode>) => void;
  /** Remove a child. */
  onRemoveChild: (childId: string) => void;
  /** Open the ActorRefPicker in rewire mode to repoint an actor_ref. */
  onRepickActorRef: (nodeId: string) => void;
  /** v0.11.1 — open FoundationRefPicker in rewire mode for orphaned
   *  mission_ref / value_ref / identity_ref. */
  onRepickFoundationRef?: (nodeId: string) => void;
  /** Remove a node entirely (used by the orphan actor_ref "Delete" action). */
  onDeleteNode: (nodeId: string) => void;
  /** Close the panel. */
  onClose: () => void;
  /** v0.7: needed for the MD editor's file paths + preview-cache hints. */
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
}

/**
 * Right-side detail panel.
 *
 * v0.2 correction (2026-04-20): composition elements (rules, contents)
 * are edited here, not as nodes on the canvas.
 */
const WIDTH_STORAGE_KEY = "plot.inspector.width";
type InspectorWidth = "narrow" | "wide";

function loadWidth(): InspectorWidth {
  if (typeof window === "undefined") return "narrow";
  const stored = window.localStorage.getItem(WIDTH_STORAGE_KEY);
  return stored === "wide" ? "wide" : "narrow";
}

export function SketchInspector({
  node,
  allNodes,
  availableActors,
  availableMissions,
  availableValues,
  availableIdentities,
  onPatchNode,
  onAddChild,
  onPatchChild,
  onRemoveChild,
  onRepickActorRef,
  onRepickFoundationRef,
  onDeleteNode,
  onClose,
  projectPath,
  projectId,
  canvasKind,
}: SketchInspectorProps) {
  const { t } = useTranslation();
  const [width, setWidth] = useState<InspectorWidth>(loadWidth);
  const toggleWidth = () => {
    const next: InspectorWidth = width === "narrow" ? "wide" : "narrow";
    setWidth(next);
    try {
      window.localStorage.setItem(WIDTH_STORAGE_KEY, next);
    } catch {
      // ignore storage quota errors; width choice is a nicety, not essential.
    }
  };
  const rules = useMemo(
    () => (node ? allNodes.filter((n) => n.parent_id === node.id && n.kind === "rule") : []),
    [node, allNodes],
  );
  const contents = useMemo(
    () => (node ? allNodes.filter((n) => n.parent_id === node.id && n.kind === "content") : []),
    [node, allNodes],
  );

  // No node selected → hide the panel entirely. The canvas was covered by an
  // empty placeholder before, but the reclaimed pixels are more useful.
  if (!node) {
    return null;
  }

  // v0.2 multi-canvas (2026-04-21): Mission / Core Value / Identity are
  // now their own node kinds on the Core canvas, so the per-root text
  // fields were removed. ``showsIdentity`` kept only for historical
  // reference; the block that used it is gone.
  // v0.12.6 — service is a category leaf in v0.12; the "root" concept no
  // longer applies to it. Only actor still carries it.
  const canToggleRoot = !node.parent_id && node.kind === "actor";
  const refTarget =
    node.kind === "actor_ref" && node.ref_actor_id
      ? availableActors.find((n) => n.id === node.ref_actor_id) ?? null
      : null;
  const isOrphanActorRef =
    node.kind === "actor_ref" && (!node.ref_actor_id || refTarget === null);

  return (
    <aside
      className={
        "pointer-events-auto absolute right-0 top-0 z-10 flex h-full flex-col border-l border-slate-200 bg-white/95 shadow-sm backdrop-blur " +
        (width === "wide" ? "w-[min(720px,60vw)]" : "w-80")
      }
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2">
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-3 w-3 shrink-0 rounded border border-slate-300"
            style={{ backgroundColor: node.color || "#ffffff" }}
            aria-hidden
          />
          <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
            {node.kind === "project"
              ? t("kind.project")
              : node.is_root && node.kind === "actor"
                ? t("kind.actorRoot")
                : node.kind
                  ? t(`kind.${node.kind}`)
                  : t("kind.node")}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {/* Delete — hidden for the Project anchor and for Actor/Service roots. */}
          {node.kind !== "project" && !node.is_root && (
            <button
              type="button"
              onClick={() => {
                if (
                  window.confirm(
                    t("inspector.confirmDelete", { name: node.label || node.id }),
                  )
                ) {
                  onDeleteNode(node.id);
                }
              }}
              aria-label={t("inspector.deleteNode")}
              className="rounded px-2 text-[10px] text-rose-600 hover:bg-rose-50"
              title={t("inspector.deleteNode")}
            >
              {t("inspector.deleteShort")}
            </button>
          )}
          <button
            type="button"
            onClick={toggleWidth}
            aria-label={
              width === "wide"
                ? t("inspector.narrowInspector")
                : t("inspector.widenInspector")
            }
            title={width === "wide" ? t("inspector.narrow") : t("inspector.widen")}
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            {width === "wide" ? "⇥" : "⇤"}
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label={t("inspector.closeInspector")}
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* v0.13 Phase 7 — MD parse warnings, surfaced first so the user
             sees the problem before editing. The list comes from the
             server's per-node template parse (collect_foundation_md_warnings). */}
        {node._md_warnings && node._md_warnings.length > 0 && (
          <div className="mb-3 rounded border border-amber-300 bg-amber-50 p-2 text-[11px] text-amber-900">
            <div className="mb-1 font-semibold">{t("inspector.mdWarnings")}</div>
            <ul className="ml-4 list-disc">
              {node._md_warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
            {node.details_path && (
              <p
                className="mt-1 text-[10px] text-amber-800"
                dangerouslySetInnerHTML={{
                  __html: t("inspector.mdWarningsFixHint", { path: node.details_path }),
                }}
              />
            )}
          </div>
        )}

        {/* Label */}
        <label className="mb-3 block">
          <span className="text-xs font-semibold text-slate-600">{t("inspector.label")}</span>
          <input
            type="text"
            value={node.label}
            onChange={(e) => onPatchNode({ label: e.target.value })}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
          />
        </label>

        {/* v0.10: Mission carries three typed fields that capture distinct
             facets — what we do (today), why (reason for being), direction
             (positioning, not time). Other kinds keep label + details.md. */}
        {node.kind === "mission" && (
          <MissionFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* v0.12 — category fields. A category is a thematic grouping;
            its only typed field is ``theme`` (one-line common thread). */}
        {node.kind === "category" && (
          <CategoryFields
            node={node}
            childCount={
              allNodes.filter(
                (n) => n.parent_id === node.id && n.kind === "service",
              ).length
            }
            onPatchNode={onPatchNode}
          />
        )}

        {/* v0.10 Step 2: Core Value typed form — definition + Do/Don't pair.
             Do/Don't follows the AI-first principle (LLMs mimic concrete
             examples better than abstract rules). Optional: blank fields
             remain blank, no validator complains. */}
        {node.kind === "core_value" && (
          <CoreValueFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* v0.10 Step 2: Identity typed form — description + Do/Don't pair. */}
        {node.kind === "identity" && (
          <IdentityFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* v0.9.1: ``label`` + per-node ``details.md`` for long-form prose. */}
        <DetailsSection
          node={node}
          projectPath={projectPath}
          projectId={projectId}
          canvasKind={canvasKind}
          onPatchNode={onPatchNode}
        />

        {/* Root toggle — only for top-level actor (v0.12.6: service is a
            category leaf in v0.12, no root semantics). */}
        {canToggleRoot && (
          <label className="mb-4 flex items-center gap-2 text-xs text-slate-700">
            <input
              type="checkbox"
              checked={node.is_root}
              onChange={(e) => onPatchNode({ is_root: e.target.checked })}
              className="accent-indigo-600"
            />
            <span>
              Mark as <strong>Actor Root</strong> (centre of its tree)
            </span>
          </label>
        )}

        {/* v0.10 Step 3: Foundation refs show their target master + a hint
             when the master is missing (orphan). No re-pick button yet —
             user can drag a fresh ref preset and delete the broken one. */}
        {(node.kind === "mission_ref" ||
          node.kind === "value_ref" ||
          node.kind === "identity_ref") && (
          <FoundationRefBlock
            node={node}
            availableMissions={availableMissions ?? []}
            availableValues={availableValues ?? []}
            availableIdentities={availableIdentities ?? []}
            onRepickFoundationRef={onRepickFoundationRef}
            onDeleteNode={onDeleteNode}
          />
        )}

        {/* v0.11.2 Phase C3: actor_ref captures per-actor-per-service value
             flow. Two free-form fields, both optional. */}
        {node.kind === "actor_ref" && (
          <ActorRefFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* Actor reference — link (or broken link) back to the Actor canvas node. */}
        {node.kind === "actor_ref" && !isOrphanActorRef && refTarget && (
          <div className="mb-4 rounded border border-pink-200 bg-pink-50/40 p-2 text-[11px]">
            <div className="mb-1 font-semibold uppercase tracking-wide text-pink-700">
              References
            </div>
            <div className="text-slate-700">
              <span className="text-slate-500">Actor:</span>{" "}
              <span className="font-medium">{refTarget.label || refTarget.id}</span>
            </div>
            <div className="mt-0.5 font-mono text-[10px] text-slate-400">
              {node.ref_actor_id}
            </div>
          </div>
        )}
        {node.kind === "actor_ref" && isOrphanActorRef && (
          <div className="mb-4 rounded border border-red-300 bg-red-50 p-2 text-[11px]">
            <div className="mb-1 font-semibold uppercase tracking-wide text-red-700">
              ⚠ Orphan — actor not found
            </div>
            <div className="mb-2 font-mono text-[10px] text-slate-500">
              ref_actor_id: {node.ref_actor_id ?? "—"}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => onRepickActorRef(node.id)}
                className="rounded border border-red-300 bg-white px-2 py-1 text-[11px] font-medium text-red-700 hover:bg-red-100"
              >
                Re-pick…
              </button>
              <button
                type="button"
                onClick={() => onDeleteNode(node.id)}
                className="rounded px-2 py-1 text-[11px] text-slate-600 hover:bg-slate-100"
              >
                Delete
              </button>
            </div>
          </div>
        )}

        {/* v0.11: Actor typed form — side / motivation / pain. */}
        {node.kind === "actor" && (
          <ActorFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* v0.10 Step 5: Metric typed form — target + measurement. */}
        {node.kind === "metric" && (
          <MetricFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* v0.10 Step 5: Step typed form — order + outcome (outcome shared
             with service kind, declared once on the model). */}
        {node.kind === "step" && (
          <StepFields node={node} onPatchNode={onPatchNode} />
        )}

        {/* v0.12.1: Service typed form — sub-service was eliminated in
             v0.12, so a service is one kind regardless of canvas. The form
             surfaces target_side + the full six typed fields (what /
             value_created / scope / trigger / how / outcome) + Do/Don't.
             All optional — design philosophy is "rich fields, minimal
             required". */}
        {node.kind === "service" && (
          <ServiceFields
            node={node}
            canvasKind={canvasKind}
            onPatchNode={onPatchNode}
          />
        )}

        {/* Service-specific composition */}
        {node.kind === "service" && (
          <>
            <CompositionList
              title="Rules"
              subtitle="policies, constraints, SLAs, permissions"
              items={rules}
              onAdd={() => onAddChild(node.id, "rule")}
              onPatch={onPatchChild}
              onRemove={onRemoveChild}
              kind="rule"
              availableActors={availableActors}
            />
            <CompositionList
              title="Contents"
              subtitle="artifacts, outputs, assets"
              items={contents}
              onAdd={() => onAddChild(node.id, "content")}
              onPatch={onPatchChild}
              onRemove={onRemoveChild}
              kind="content"
              availableActors={availableActors}
            />
          </>
        )}

        {/* Actor placeholder — v0.3 fields land here */}
        {node.kind === "actor" && !node.is_root && (
          <div className="rounded border border-dashed border-slate-300 p-3 text-xs italic text-slate-400">
            Actor composition (permissions / capabilities / goals / state) lands in v0.3.
          </div>
        )}
      </div>
    </aside>
  );
}

interface CompositionListProps {
  title: string;
  subtitle: string;
  items: SketchNode[];
  onAdd: () => void;
  onPatch: (childId: string, patch: Partial<SketchNode>) => void;
  onRemove: (childId: string) => void;
  /** v0.10 Step 6: which kind this list is for. The expanded form
   *  shows kind-specific typed fields (rule → policy + permissions,
   *  content → format + producer/consumer). */
  kind: "rule" | "content";
  /** v0.10 Step 6: actor masters used by rule's permission editor and
   *  by content's producer/consumer pickers. */
  availableActors?: SketchNode[];
}

function CompositionList({
  title,
  subtitle,
  items,
  onAdd,
  onPatch,
  onRemove,
  kind,
  availableActors,
}: CompositionListProps) {
  return (
    <div className="mb-4">
      <div className="mb-1 flex items-baseline justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-700">{title}</div>
          <div className="text-[10px] italic text-slate-400">{subtitle}</div>
        </div>
        <button
          type="button"
          onClick={onAdd}
          className="rounded bg-slate-900 px-2 py-0.5 text-[10px] font-medium text-white hover:bg-slate-700"
        >
          + Add
        </button>
      </div>
      {items.length === 0 ? (
        <div className="rounded border border-dashed border-slate-200 p-2 text-[11px] italic text-slate-400">
          (none)
        </div>
      ) : (
        <ul className="space-y-1">
          {items.map((item) => (
            <CompositionRow
              key={item.id}
              item={item}
              kind={kind}
              availableActors={availableActors}
              onPatch={onPatch}
              onRemove={onRemove}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

interface CompositionRowProps {
  item: SketchNode;
  kind: "rule" | "content";
  availableActors?: SketchNode[];
  onPatch: (childId: string, patch: Partial<SketchNode>) => void;
  onRemove: (childId: string) => void;
}

function CompositionRow({
  item,
  kind,
  availableActors,
  onPatch,
  onRemove,
}: CompositionRowProps) {
  const [expanded, setExpanded] = useState(false);
  return (
    <li className="group rounded border border-slate-200 bg-white">
      <div className="flex items-start gap-1 px-2 py-1">
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="rounded px-1 text-[10px] text-slate-500 hover:bg-slate-100"
          aria-label={expanded ? "Collapse" : "Expand"}
          title={expanded ? "Collapse" : "Expand"}
        >
          {expanded ? "▾" : "▸"}
        </button>
        <div className="flex-1">
          <input
            type="text"
            value={item.label}
            onChange={(e) => onPatch(item.id, { label: e.target.value })}
            placeholder="Name"
            className="w-full border-none bg-transparent text-xs font-medium text-slate-800 focus:outline-none"
          />
        </div>
        <button
          type="button"
          onClick={() => {
            if (window.confirm(`Remove "${item.label || "(untitled)"}"?`)) {
              onRemove(item.id);
            }
          }}
          className="rounded px-1 text-[10px] text-rose-600 opacity-0 hover:bg-rose-50 group-hover:opacity-100"
          aria-label="Remove"
        >
          ✕
        </button>
      </div>
      {expanded && (
        <div className="border-t border-slate-100 px-2 py-2">
          {kind === "rule" ? (
            <RuleFields
              node={item}
              availableActors={availableActors ?? []}
              onPatchNode={(patch) => onPatch(item.id, patch)}
            />
          ) : (
            <ContentFields
              node={item}
              availableActors={availableActors ?? []}
              onPatchNode={(patch) => onPatch(item.id, patch)}
            />
          )}
        </div>
      )}
    </li>
  );
}

// ---------------------------------------------------------------------------
// v0.10 Mission typed fields
// ---------------------------------------------------------------------------
//
// Mission has three distinct facets that are too domain-specific to collapse
// into a single label or free-form prose:
//   - what_we_do: current-tense daily activity ("우리는 매일 …")
//   - why: reason for being ("사람들이 …하기를 바라서")
//   - direction: positioning, space-axis (Vision/Goal is the time-axis,
//                handled separately).
// LLMs benefit from typed fields over free prose, and human authors are
// nudged to address all three facets explicitly. See docs/CONCEPTS.md.

// v0.12 — category typed field: one-line theme.

interface CategoryFieldsProps {
  node: SketchNode;
  /** v0.12.6: number of services nested under this category. 0 → soft
   *  warning that the category is currently empty. */
  childCount: number;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function CategoryFields({ node, childCount, onPatchNode }: CategoryFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-slate-200 bg-slate-50/60 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-slate-700">
        {t("kind.category")}
      </div>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.theme")}</span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.theme")}
        </span>
        <textarea
          rows={2}
          value={node.theme ?? ""}
          onChange={(e) => onPatchNode({ theme: e.target.value })}
          placeholder="이 카테고리의 공통 주제 / 묶음의 본질"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-slate-600 focus:outline-none"
        />
      </label>
      {childCount === 0 && (
        <p className="mt-2 rounded border border-amber-300 bg-amber-50 px-2 py-1 text-[11px] text-amber-800">
          이 카테고리에 service 가 없습니다. category 는 service 를 묶기 위해
          존재 — 비어있으면 시각 노이즈입니다. service 를 추가하거나 카테고리를
          삭제하세요.
        </p>
      )}
    </div>
  );
}

interface MissionFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function MissionFields({ node, onPatchNode }: MissionFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-indigo-200 bg-indigo-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-indigo-700">
        {t("kind.mission")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.whatWeDo")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.whatWeDo")}
        </span>
        <textarea
          rows={2}
          value={node.what_we_do ?? ""}
          onChange={(e) => onPatchNode({ what_we_do: e.target.value })}
          placeholder="우리는 매일 …"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.why")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.why")}</span>
        <textarea
          rows={2}
          value={node.why ?? ""}
          onChange={(e) => onPatchNode({ why: e.target.value })}
          placeholder="사람들이 … 하기를 바라서"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.direction")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.direction")}
        </span>
        <textarea
          rows={2}
          value={node.direction ?? ""}
          onChange={(e) => onPatchNode({ direction: e.target.value })}
          placeholder="누구나 … 인 일상으로"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
    </div>
  );
}

// ---------------------------------------------------------------------------
// v0.12.1 — Service typed fields
// ---------------------------------------------------------------------------
//
// Sub-service was eliminated in v0.12 — service is now a leaf inside a
// category, and the per-service modal (service_detail canvas) hosts the
// composition. Both contexts surface the same field set: target_side +
// six typed fields (what / value_created / scope / trigger / how /
// outcome) + do/dont. All optional.

interface ServiceFieldsProps {
  node: SketchNode;
  canvasKind: CanvasKind;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ServiceFields({ node, onPatchNode }: ServiceFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-sky-200 bg-sky-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-sky-700">
        {t("kind.service")}
      </div>
      {/* v0.11.4 — target_side classifies the service by which side of the
          value exchange it exists for. Mirror of actor.side. */}
      <label className="mb-3 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.targetSide")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.targetSide")}
        </span>
        <select
          value={node.target_side ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onPatchNode({
              target_side:
                v === "operator" || v === "user" || v === "both" ? v : null,
            });
          }}
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-sky-600 focus:outline-none"
        >
          <option value="">{t("inspector.unset")}</option>
          <option value="operator">{t("inspector.operatorSideOption")}</option>
          <option value="user">{t("inspector.userSideOption")}</option>
          <option value="both">{t("inspector.bothSideOption")}</option>
        </select>
      </label>
      <ServiceTextarea
        label={t("inspector.field.what")}
        hint={t("inspector.fieldHint.what")}
        value={node.what}
        onChange={(v) => onPatchNode({ what: v })}
        placeholder="이 서비스는…"
      />
      <ServiceTextarea
        label={t("inspector.field.valueCreated")}
        hint={t("inspector.fieldHint.valueCreated")}
        value={node.value_created}
        onChange={(v) => onPatchNode({ value_created: v })}
        placeholder="만들어내는 가치"
      />
      <ServiceTextarea
        label={t("inspector.field.scope")}
        hint={t("inspector.fieldHint.scope")}
        value={node.scope}
        onChange={(v) => onPatchNode({ scope: v })}
        placeholder="포함/제외 범위"
      />
      <ServiceTextarea
        label={t("inspector.field.trigger")}
        hint={t("inspector.fieldHint.trigger")}
        value={node.trigger}
        onChange={(v) => onPatchNode({ trigger: v })}
        placeholder="언제/무엇으로 시작?"
      />
      <ServiceTextarea
        label={t("inspector.field.how")}
        hint={t("inspector.fieldHint.how")}
        value={node.how}
        onChange={(v) => onPatchNode({ how: v })}
        placeholder="어떻게 동작?"
      />
      <ServiceTextarea
        label={t("inspector.field.outcome")}
        hint={t("inspector.fieldHint.outcome")}
        value={node.outcome}
        onChange={(v) => onPatchNode({ outcome: v })}
        placeholder="끝나면 어떤 상태?"
      />
      <DoDontFields node={node} onPatchNode={onPatchNode} />
    </div>
  );
}

interface ServiceTextareaProps {
  label: string;
  hint: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}

function ServiceTextarea({
  label,
  hint,
  value,
  onChange,
  placeholder,
}: ServiceTextareaProps) {
  return (
    <label className="mb-2 block">
      <span className="text-xs font-semibold text-slate-700">{label}</span>
      <span className="ml-1 text-[10px] text-slate-500">— {hint}</span>
      <textarea
        rows={2}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-sky-600 focus:outline-none"
      />
    </label>
  );
}

// ---------------------------------------------------------------------------
// v0.10 Step 6 — rule + content typed-field polish
// ---------------------------------------------------------------------------
//
// Rules carry a policy statement, an enforcement note, and an optional
// actor → permission map (e.g. {"user": "RUD", "admin": "CRUD"}). The
// permission string is free-form; the suggested vocabulary is C/R/U/D.
//
// Contents carry a format hint and producer/consumer actor master ids.
// The pickers list ``availableActors`` (the actor masters from the
// Actors canvas), so picking is consistent with actor_ref semantics.

interface RuleFieldsProps {
  node: SketchNode;
  availableActors: SketchNode[];
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function RuleFields({ node, availableActors, onPatchNode }: RuleFieldsProps) {
  const { t } = useTranslation();
  const permissions = node.actor_permissions ?? {};
  const usedIds = new Set(Object.keys(permissions));
  const candidates = availableActors.filter((a) => !usedIds.has(a.id));
  return (
    <div className="text-xs">
      <label className="mb-2 block">
        <span className="font-semibold text-slate-700">{t("inspector.field.policy")}</span>
        <textarea
          rows={2}
          value={node.policy ?? ""}
          onChange={(e) => onPatchNode({ policy: e.target.value })}
          placeholder="이 룰이 강제하는 것"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 focus:border-stone-500 focus:outline-none"
        />
      </label>
      <label className="mb-2 block">
        <span className="font-semibold text-slate-700">{t("inspector.field.enforcement")}</span>
        <textarea
          rows={2}
          value={node.enforcement ?? ""}
          onChange={(e) => onPatchNode({ enforcement: e.target.value })}
          placeholder="어디서/어떻게 강제?"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 focus:border-stone-500 focus:outline-none"
        />
      </label>
      <div className="mt-2">
        <div className="mb-1 font-semibold text-slate-700">
          {t("inspector.field.actorPermissions")}
        </div>
        <div
          className="mb-1 text-[10px] italic text-slate-400"
          dangerouslySetInnerHTML={{
            __html: t("inspector.fieldHint.actorPermissionsShorthand"),
          }}
        />

        {Object.entries(permissions).length === 0 && (
          <div className="rounded border border-dashed border-slate-200 p-1.5 text-[11px] italic text-slate-400">
            {t("inspector.empty")}
          </div>
        )}
        <ul className="space-y-1">
          {Object.entries(permissions).map(([actorId, perm]) => {
            const actor = availableActors.find((a) => a.id === actorId);
            return (
              <li key={actorId} className="flex items-center gap-1">
                <span
                  className="flex-1 truncate text-[11px] text-slate-700"
                  title={actorId}
                >
                  {actor?.label || actorId}
                </span>
                <input
                  type="text"
                  value={perm}
                  onChange={(e) =>
                    onPatchNode({
                      actor_permissions: {
                        ...permissions,
                        [actorId]: e.target.value,
                      },
                    })
                  }
                  placeholder="CRUD"
                  className="w-20 rounded border border-slate-300 px-1.5 py-0.5 text-[11px] focus:border-stone-500 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => {
                    const next = { ...permissions };
                    delete next[actorId];
                    onPatchNode({ actor_permissions: next });
                  }}
                  className="rounded px-1 text-[10px] text-rose-600 hover:bg-rose-50"
                  aria-label={t("inspector.permissionRemove")}
                >
                  ✕
                </button>
              </li>
            );
          })}
        </ul>
        {candidates.length > 0 && (
          <select
            value=""
            onChange={(e) => {
              const id = e.target.value;
              if (!id) return;
              onPatchNode({
                actor_permissions: { ...permissions, [id]: "" },
              });
            }}
            className="mt-1 w-full rounded border border-slate-300 px-1.5 py-0.5 text-[11px] focus:border-stone-500 focus:outline-none"
          >
            <option value="">{t("inspector.addActorPermission")}</option>
            {candidates.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label || a.id}
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  );
}

interface ContentFieldsProps {
  node: SketchNode;
  availableActors: SketchNode[];
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ContentFields({
  node,
  availableActors,
  onPatchNode,
}: ContentFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="text-xs">
      <label className="mb-2 block">
        <span className="font-semibold text-slate-700">{t("inspector.field.format")}</span>
        <input
          type="text"
          value={node.format ?? ""}
          onChange={(e) => onPatchNode({ format: e.target.value })}
          placeholder="JSON / MD / image / token …"
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 focus:border-violet-500 focus:outline-none"
        />
      </label>
      <ContentActorPicker
        label={t("inspector.field.producer")}
        hint={t("inspector.fieldHint.producer")}
        actorId={node.producer_actor_id}
        availableActors={availableActors}
        onChange={(id) => onPatchNode({ producer_actor_id: id })}
      />
      <ContentActorPicker
        label={t("inspector.field.consumer")}
        hint={t("inspector.fieldHint.consumer")}
        actorId={node.consumer_actor_id}
        availableActors={availableActors}
        onChange={(id) => onPatchNode({ consumer_actor_id: id })}
      />
    </div>
  );
}

interface ContentActorPickerProps {
  label: string;
  hint: string;
  actorId: string | null;
  availableActors: SketchNode[];
  onChange: (id: string | null) => void;
}

function ContentActorPicker({
  label,
  hint,
  actorId,
  availableActors,
  onChange,
}: ContentActorPickerProps) {
  const { t } = useTranslation();
  return (
    <label className="mb-2 block">
      <span className="font-semibold text-slate-700">{label}</span>
      <span className="ml-1 text-[10px] text-slate-500">— {hint}</span>
      <select
        value={actorId ?? ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="mt-1 w-full rounded border border-slate-300 px-2 py-1 focus:border-violet-500 focus:outline-none"
      >
        <option value="">{t("inspector.unset")}</option>
        {availableActors.map((a) => (
          <option key={a.id} value={a.id}>
            {a.label || a.id}
          </option>
        ))}
      </select>
    </label>
  );
}

// ---------------------------------------------------------------------------
// v0.11.2 Phase C3 — actor_ref value flow (gives / receives)
// ---------------------------------------------------------------------------
//
// Per-actor-per-service value flow on the ref node itself (rather than on
// an explicit edge). PHILOSOPHY.md P6 ("arrows carry action and value")
// in its weakened form: the value lives on the ref node, the arrow is the
// implicit "this actor participates in this service" relationship.
// service.value_created is the aggregate; gives/receives is each actor's
// individual exchange with this service.

interface ActorRefFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ActorRefFields({ node, onPatchNode }: ActorRefFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-pink-200 bg-pink-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-pink-700">
        {t("inspector.valueFlowHeader")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-emerald-700">{t("inspector.field.gives")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.gives")}</span>
        <textarea
          rows={2}
          value={node.gives ?? ""}
          onChange={(e) => onPatchNode({ gives: e.target.value })}
          placeholder="콘텐츠 / 시간 / 결제 / 주의 …"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-emerald-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-violet-700">
          {t("inspector.field.receives")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.receives")}
        </span>
        <textarea
          rows={2}
          value={node.receives ?? ""}
          onChange={(e) => onPatchNode({ receives: e.target.value })}
          placeholder="피드백 / 신뢰 / 접근권 / 즐거움 …"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-violet-600 focus:outline-none"
        />
      </label>
    </div>
  );
}

// ---------------------------------------------------------------------------
// v0.11 — Actor typed fields (side / motivation / pain)
// ---------------------------------------------------------------------------
//
// See plot/docs/IDENTITY.md "Actor & Service — the Core Philosophy".
// `side` partitions an actor by which side of the value exchange they
// occupy (operator vs user). `motivation` + `pain` use the standard
// persona-design pair: motivation pulls the actor in, pain pushes them.

interface ActorFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ActorFields({ node, onPatchNode }: ActorFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-rose-200 bg-rose-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-rose-700">
        {t("kind.actor")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.side")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.side")}</span>
        <select
          value={node.side ?? ""}
          onChange={(e) =>
            onPatchNode({
              side: e.target.value === "" ? null : (e.target.value as "operator" | "user"),
            })
          }
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        >
          <option value="">{t("inspector.unset")}</option>
          <option value="operator">{t("inspector.operatorOption")}</option>
          <option value="user">{t("inspector.userOption")}</option>
        </select>
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.motivation")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.motivation")}
        </span>
        <textarea
          rows={2}
          value={node.motivation ?? ""}
          onChange={(e) => onPatchNode({ motivation: e.target.value })}
          placeholder="이 액터가 무엇을 얻으려 하는가"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.pain")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.pain")}</span>
        <textarea
          rows={2}
          value={node.pain ?? ""}
          onChange={(e) => onPatchNode({ pain: e.target.value })}
          placeholder="겪는 어려움 / 좌절"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        />
      </label>
    </div>
  );
}

// ---------------------------------------------------------------------------
// v0.10 Step 5 — metric + step composition typed fields
// ---------------------------------------------------------------------------

interface MetricFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function MetricFields({ node, onPatchNode }: MetricFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-lime-200 bg-lime-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-lime-700">
        {t("kind.metric")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.target")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.target")}</span>
        <input
          type="text"
          value={node.target ?? ""}
          onChange={(e) => onPatchNode({ target: e.target.value })}
          placeholder=">99% / under 200ms / …"
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-lime-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.measurement")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.measurement")}
        </span>
        <textarea
          rows={2}
          value={node.measurement ?? ""}
          onChange={(e) => onPatchNode({ measurement: e.target.value })}
          placeholder="어떤 신호를 어떻게 집계?"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-lime-600 focus:outline-none"
        />
      </label>
    </div>
  );
}

interface StepFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function StepFields({ node, onPatchNode }: StepFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-indigo-200 bg-indigo-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-indigo-700">
        {t("kind.step")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.order")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.order")}</span>
        <input
          type="number"
          value={node.order ?? ""}
          onChange={(e) => {
            const raw = e.target.value;
            onPatchNode({ order: raw === "" ? null : Number(raw) });
          }}
          placeholder="1, 2, 3, …"
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.outcome")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.outcome")}
        </span>
        <textarea
          rows={2}
          value={node.outcome ?? ""}
          onChange={(e) => onPatchNode({ outcome: e.target.value })}
          placeholder="이 단계 끝나면 어떤 상태?"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
    </div>
  );
}

// ---------------------------------------------------------------------------
// v0.10 Step 3 — Foundation reference display (mission_ref / value_ref / identity_ref)
// ---------------------------------------------------------------------------

interface FoundationRefBlockProps {
  node: SketchNode;
  availableMissions: SketchNode[];
  availableValues: SketchNode[];
  availableIdentities: SketchNode[];
  /** v0.11.1 — opens FoundationRefPicker in rewire mode for the given node. */
  onRepickFoundationRef?: (nodeId: string) => void;
  /** v0.11.1 — delete the orphan ref outright. */
  onDeleteNode?: (nodeId: string) => void;
}

function FoundationRefBlock({
  node,
  availableMissions,
  availableValues,
  availableIdentities,
  onRepickFoundationRef,
  onDeleteNode,
}: FoundationRefBlockProps) {
  const { t } = useTranslation();
  let label: string;
  let id: string | null;
  let masters: SketchNode[];
  let tone: { fg: string; bg: string };
  if (node.kind === "mission_ref") {
    label = t("kind.mission");
    id = node.ref_mission_id;
    masters = availableMissions;
    tone = { fg: "text-amber-700", bg: "border-amber-200 bg-amber-50/40" };
  } else if (node.kind === "value_ref") {
    label = t("kind.core_value");
    id = node.ref_value_id;
    masters = availableValues;
    tone = { fg: "text-yellow-700", bg: "border-yellow-200 bg-yellow-50/40" };
  } else {
    label = t("kind.identity");
    id = node.ref_identity_id;
    masters = availableIdentities;
    tone = { fg: "text-orange-700", bg: "border-orange-200 bg-orange-50/40" };
  }
  const target = id ? masters.find((m) => m.id === id) ?? null : null;
  const orphan = !id || target === null;
  return (
    <div className={`mb-4 rounded border p-2 text-[11px] ${tone.bg}`}>
      <div className={`mb-1 font-semibold uppercase tracking-wide ${tone.fg}`}>
        {t("inspector.referencesHeader", { label })}
      </div>
      {orphan ? (
        <>
          <div className="text-rose-700">{t("inspector.masterNotFound")}</div>
          <div className="mb-2 font-mono text-[10px] text-slate-500">
            id: {id ?? "—"}
          </div>
          {(onRepickFoundationRef || onDeleteNode) && (
            <div className="flex gap-2">
              {onRepickFoundationRef && (
                <button
                  type="button"
                  onClick={() => onRepickFoundationRef(node.id)}
                  className="rounded border border-rose-300 bg-white px-2 py-1 text-[11px] font-medium text-rose-700 hover:bg-rose-100"
                >
                  {t("inspector.rePick")}
                </button>
              )}
              {onDeleteNode && (
                <button
                  type="button"
                  onClick={() => onDeleteNode(node.id)}
                  className="rounded px-2 py-1 text-[11px] text-slate-600 hover:bg-slate-100"
                >
                  {t("common.delete")}
                </button>
              )}
            </div>
          )}
        </>
      ) : (
        <>
          <div className="text-slate-700">
            <span className="text-slate-500">{label}:</span>{" "}
            <span className="font-medium">{target.label || target.id}</span>
          </div>
          <div className="mt-0.5 font-mono text-[10px] text-slate-400">{id}</div>
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// v0.10 Step 2 — Core Value + Identity typed fields
// ---------------------------------------------------------------------------
//
// Core Value answers "how do we behave under conflict?" Identity answers
// "how do we look and sound?" Both benefit from a Do/Don't pair: LLMs that
// help simulate behaviour or write copy in the project's voice reach for
// concrete examples first, abstract rules second.

interface CoreValueFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function CoreValueFields({ node, onPatchNode }: CoreValueFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-amber-200 bg-amber-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-amber-700">
        {t("kind.core_value")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.definition")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.definition")}
        </span>
        <textarea
          rows={2}
          value={node.definition ?? ""}
          onChange={(e) => onPatchNode({ definition: e.target.value })}
          placeholder="한두 문장으로"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <DoDontFields node={node} onPatchNode={onPatchNode} />
    </div>
  );
}

interface IdentityFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function IdentityFields({ node, onPatchNode }: IdentityFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-violet-200 bg-violet-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-violet-700">
        {t("kind.identity")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.description")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.description")}
        </span>
        <textarea
          rows={2}
          value={node.description ?? ""}
          onChange={(e) => onPatchNode({ description: e.target.value })}
          placeholder="이 속성이 어떻게 드러나는가"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <DoDontFields node={node} onPatchNode={onPatchNode} />
    </div>
  );
}

interface DoDontFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function DoDontFields({ node, onPatchNode }: DoDontFieldsProps) {
  const { t } = useTranslation();
  return (
    <>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-emerald-700">{t("inspector.field.do")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.do")}</span>
        <textarea
          rows={2}
          value={node.do ?? ""}
          onChange={(e) => onPatchNode({ do: e.target.value })}
          placeholder="이렇게 행동/표현한다"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-emerald-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-rose-700">{t("inspector.field.dont")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.dont")}</span>
        <textarea
          rows={2}
          value={node.dont ?? ""}
          onChange={(e) => onPatchNode({ dont: e.target.value })}
          placeholder="이렇게는 안 한다"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        />
      </label>
    </>
  );
}

// ---------------------------------------------------------------------------
// v0.9.1 details.md section — the only content surface
// ---------------------------------------------------------------------------
//
// Long-form prose lives in a per-node ``details.md`` file. JSON keeps no
// mirror, so external editors (Obsidian, VS Code) can edit the same file
// without sync conflicts — the watcher just nudges open viewers to reload.

interface DetailsSectionProps {
  node: SketchNode;
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function DetailsSection({
  node,
  projectPath,
  projectId,
  canvasKind,
  onPatchNode,
}: DetailsSectionProps) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  if (node.details_path) {
    return (
      <div className="-mx-3 mb-4 h-[50vh] border-y border-slate-200">
        <MDFileEditor
          projectPath={projectPath}
          path={node.details_path}
          projectId={projectId}
          nodeId={node.id}
          canvasKind={canvasKind}
        />
      </div>
    );
  }

  const onCreate = async () => {
    if (busy) return;
    setBusy(true);
    setErr(null);
    try {
      const canvasSlug = canvasKind;
      const desired = node.kind
        ? folderSlug(node.kind, node.label || node.kind, canvasSlug)
        : `${canvasSlug}/${node.id}`;
      const actualPath = await createFolder(projectPath, projectId, desired);
      // Server seeds an empty ``index.md``; v0.9 wants the file named
      // ``details.md`` instead. Convention: use ``${actualPath}/details.md``.
      onPatchNode({ details_path: `${actualPath}/details.md` });
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mb-4 rounded border border-dashed border-slate-300 p-2 text-xs">
      <div className="mb-1 font-semibold text-slate-600">Long-form details</div>
      <div className="mb-2 text-[11px] text-slate-500">
        긴 글, 표, Mermaid 다이어그램이 필요하면 별도 MD 파일을 만드세요.
        외부 에디터(Obsidian, VS Code)에서도 같은 파일을 직접 편집할 수 있어요.
      </div>
      <button
        type="button"
        onClick={onCreate}
        disabled={busy}
        className="rounded bg-slate-900 px-2 py-1 text-[11px] font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {busy ? "Creating…" : "📁 Create details"}
      </button>
      {err && <div className="mt-2 text-[11px] text-rose-600">{err}</div>}
    </div>
  );
}
