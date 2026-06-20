/**
 * D-2026-06-15-J — actor motivation/pain become per-service-context.
 *
 * PHILOSOPHY P3 (Participation is Asymmetric): the same human is a Hero
 * in one service and a Fan in another, so motivation/pain are defined
 * BY the service, not globally. They move OFF the actor entity (identity:
 * side + body) and ONTO actor_ref (per-service stake, alongside the
 * existing gives/receives). PURE per-service — no actor-level baseline.
 */
import { describe, expect, it } from "vitest";
import { Actor } from "../src/domain/Actor";
import { ActorRef } from "../src/domain/ActorRef";
import { effectiveActorFields } from "../src/domain/actorInheritance";
import type { SketchEdge, SketchNode } from "../src/types";

const BASE = {
  id: "n1",
  label: "L",
  x: 0,
  y: 0,
  width: 80,
  height: 36,
  color: "#fff",
  shape: "rounded",
  icon: null,
  collapsed: false,
  is_root: false,
  details_path: null,
  owner: null,
  version: "v1.0",
};

function inheritEdge(child: string, parent: string): SketchEdge {
  return {
    id: `e_${child}_${parent}`,
    source: child,
    target: parent,
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    directed: true,
    relation: "inheritance",
    action_verb: null,
    value_form: [],
  } as SketchEdge;
}

describe("D-2026-06-19-I — actor_ref = read-only anchor (per-service stake retired)", () => {
  it("actor_ref carries only ref_actor_id + side; gives/receives/motivation/pain are gone", () => {
    const ref = ActorRef.fromJson({
      ...BASE,
      kind: "actor_ref",
      ref_actor_id: "a1",
      // legacy per-service-stake fields — must be DROPPED on read (discard)
      gives: "time",
      receives: "fame",
      motivation: "wants reach here",
      pain: "upload is slow",
      side: "user",
    });
    expect(ref.ref_actor_id).toBe("a1");
    expect(ref.side).toBe("user");
    const json = ref.toJson() as Record<string, unknown>;
    for (const gone of ["gives", "receives", "motivation", "pain"]) {
      expect(gone in json).toBe(false);
    }
  });

  it("actor no longer carries motivation/pain (identity only: side + body)", () => {
    const a = Actor.fromJson({ ...BASE, kind: "actor", side: "user", body: "who they are" });
    const json = a.toJson() as Record<string, unknown>;
    expect("motivation" in json).toBe(false);
    expect("pain" in json).toBe(false);
    expect(json.side).toBe("user");
    expect(json.body).toBe("who they are");
  });

  it("effectiveActorFields resolves only side + body (motivation/pain gone)", () => {
    const nodes = [
      { ...BASE, id: "user", label: "User", kind: "actor", side: "user", body: "base body" },
      { ...BASE, id: "op", label: "Operator", kind: "actor", side: null, body: "" },
    ] as unknown as SketchNode[];
    const eff = effectiveActorFields("op", nodes, [
      inheritEdge("op", "user"),
    ]) as unknown as Record<string, unknown>;
    expect((eff.side as { value: string }).value).toBe("user");
    expect((eff.body as { value: string }).value).toBe("base body");
    expect("motivation" in eff).toBe(false);
    expect("pain" in eff).toBe(false);
  });
});
