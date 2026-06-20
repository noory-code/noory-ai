/**
 * Per-kind entity-class round-trip + parseEntity dispatch tests.
 *
 * Each Phase 2.X commit lands one entity class and adds its tests
 * here. The pattern is the same:
 *
 *   1. ``Class.fromJson(rawJson)`` builds the entity.
 *   2. ``entity.toJson()`` serialises back.
 *   3. ``Class.fromJson(entity.toJson())`` deep-equals the original.
 *   4. ``parseEntity(rawJson)`` dispatches to the right class.
 *
 * Mirrors the server-side ``plot/tests/test_node_models.py`` pattern.
 */
import { describe, expect, it } from "vitest";
import {
  Actor,
  ActorRef,
  Category,
  CoreValue,
  DomainParseError,
  Identity,
  Mission,
  parseEntity,
  Project,
  Rule,
  Service,
  Step,
} from "../../src/domain";

// metric retired 2026-06-20 (D-2026-06-20-H).

describe("Step.fromJson + toJson round-trip", () => {
  it("populates defaults from a minimal raw", () => {
    const s = Step.fromJson({ id: "s1", kind: "step" });
    expect(s.kind).toBe("step");
    expect(s.order).toBeNull();
    expect(s.outcome).toBe("");
  });

  it("preserves an explicit ordered step", () => {
    const s = Step.fromJson({ id: "s1", kind: "step", order: 3, outcome: "session" });
    expect(s.order).toBe(3);
    expect(s.outcome).toBe("session");
  });

  it("rejects fractional order", () => {
    expect(() => Step.fromJson({ id: "s1", kind: "step", order: 1.5 })).toThrow(DomainParseError);
  });

  it("rejects raw with the wrong kind", () => {
    expect(() => Step.fromJson({ id: "s1", kind: "rule" })).toThrow(DomainParseError);
  });

  it("survives full round-trip with order=null (parallel branch)", () => {
    const a = Step.fromJson({ id: "s1", kind: "step", outcome: "x" });
    const b = Step.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });
});

describe("parseEntity → Step dispatch", () => {
  it("returns a Step instance for kind=\"step\"", () => {
    const node = parseEntity({ id: "s1", kind: "step", order: 1 });
    expect(node).toBeInstanceOf(Step);
    expect((node as Step).order).toBe(1);
  });
});

describe("CoreValue.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const cv = CoreValue.fromJson({ id: "cv1", kind: "core_value" });
    expect(cv.kind).toBe("core_value");
    expect(cv.definition).toBe("");
    expect(cv.body).toBe("");
  });

  it("preserves definition + body and round-trips", () => {
    const a = CoreValue.fromJson({
      id: "cv1",
      kind: "core_value",
      definition: "관용",
      body: "판단 기준: 상대를 이해하려 했는가?",
    });
    const b = CoreValue.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("migrates legacy do/dont → body (v0.43.1)", () => {
    const cv = CoreValue.fromJson({
      id: "cv1",
      kind: "core_value",
      definition: "관용",
      do: "다른 의견을 먼저 듣는다",
      dont: "비난부터 한다",
      body: "원래 본문",
    });
    expect(cv.definition).toBe("관용");
    expect(cv.body).toContain("원래 본문");
    expect(cv.body).toContain("다른 의견을 먼저 듣는다");
    expect(cv.body).toContain("비난부터 한다");
    expect("do" in cv).toBe(false);
  });

  it("rejects raw with the wrong kind", () => {
    expect(() => CoreValue.fromJson({ id: "cv1", kind: "rule" })).toThrow(DomainParseError);
  });
});

describe("Identity.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const id = Identity.fromJson({ id: "id1", kind: "identity" });
    expect(id.kind).toBe("identity");
    expect(id.description).toBe("");
    expect(id.body).toBe("");
  });

  it("preserves description + body and round-trips", () => {
    const a = Identity.fromJson({
      id: "id1",
      kind: "identity",
      label: "Voice",
      description: "따뜻하고 진솔하게",
      body: "이름을 부른다",
    });
    const b = Identity.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("migrates legacy do/dont → body (v0.43.2)", () => {
    const id = Identity.fromJson({
      id: "id1",
      kind: "identity",
      description: "따뜻하게",
      do: "이름을 부른다",
      dont: "공지글 같은 말투로",
      body: "원래 본문",
    });
    expect(id.description).toBe("따뜻하게");
    expect(id.body).toContain("원래 본문");
    expect(id.body).toContain("이름을 부른다");
    expect(id.body).toContain("공지글 같은 말투로");
    expect("do" in id).toBe(false);
  });

  // Output model — status + provenance (v0.44.0, D-2026-06-07-A)
  it("defaults the output fields (graceful degradation)", () => {
    const id = Identity.fromJson({ id: "id1", kind: "identity" });
    expect(id.status).toBe("manual");
    expect(id.provenance).toEqual([]);
  });

  it("preserves + round-trips status + provenance", () => {
    const a = Identity.fromJson({
      id: "id1",
      kind: "identity",
      description: "warm",
      status: "confirmed",
      provenance: ["mission-1", "core_value-2"],
    });
    expect(a.status).toBe("confirmed");
    expect(a.provenance).toEqual(["mission-1", "core_value-2"]);
    const b = Identity.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects an unknown status value", () => {
    expect(() =>
      Identity.fromJson({ id: "id1", kind: "identity", status: "bogus" }),
    ).toThrow();
  });

  it("rejects a non-string-array provenance", () => {
    expect(() =>
      Identity.fromJson({ id: "id1", kind: "identity", provenance: [1, 2] }),
    ).toThrow();
  });
});

describe("parseEntity → Foundation kinds dispatch", () => {
  it("dispatches core_value to CoreValue", () => {
    const node = parseEntity({ id: "cv1", kind: "core_value", definition: "x" });
    expect(node).toBeInstanceOf(CoreValue);
  });

  it("dispatches identity to Identity", () => {
    const node = parseEntity({ id: "id1", kind: "identity", description: "x" });
    expect(node).toBeInstanceOf(Identity);
  });
});

describe("Project.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const p = Project.fromJson({ id: "project", kind: "project" });
    expect(p.kind).toBe("project");
    expect(p.label).toBe("");
  });

  it("round-trips through parseEntity", () => {
    const node = parseEntity({ id: "project", kind: "project", label: "Plot" });
    expect(node).toBeInstanceOf(Project);
    expect(node.label).toBe("Plot");
  });

  it("rejects raw with the wrong kind", () => {
    expect(() => Project.fromJson({ id: "x", kind: "actor" })).toThrow(DomainParseError);
  });
});

describe("Category.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const c = Category.fromJson({ id: "cat-1", kind: "category" });
    expect(c.kind).toBe("category");
    expect(c.theme).toBe("");
  });

  it("preserves theme and round-trips", () => {
    const a = Category.fromJson({
      id: "cat-1",
      kind: "category",
      label: "Admin",
      theme: "operator system management",
    });
    const b = Category.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects non-string theme", () => {
    expect(() => Category.fromJson({ id: "c", kind: "category", theme: 42 })).toThrow(
      DomainParseError,
    );
  });

  it("dispatches via parseEntity", () => {
    const node = parseEntity({ id: "c", kind: "category", theme: "x" });
    expect(node).toBeInstanceOf(Category);
  });
});

describe("ActorRef.fromJson + toJson round-trip (read-only anchor, D-2026-06-19-I)", () => {
  it("populates defaults (ref_actor_id + side only)", () => {
    const r = ActorRef.fromJson({ id: "ref-1", kind: "actor_ref" });
    expect(r.kind).toBe("actor_ref");
    expect(r.ref_actor_id).toBeNull();
    expect(r.side).toBeNull();
  });

  it("preserves ref + side and round-trips; drops retired stake fields", () => {
    const a = ActorRef.fromJson({
      id: "ref-1",
      kind: "actor_ref",
      ref_actor_id: "operator",
      // legacy per-service stake — dropped on read
      gives: "moderation",
      receives: "reputation",
      motivation: "x",
      pain: "y",
      side: "operator",
    });
    expect(a.ref_actor_id).toBe("operator");
    expect(a.side).toBe("operator");
    const json = a.toJson() as Record<string, unknown>;
    for (const gone of ["gives", "receives", "motivation", "pain"]) {
      expect(gone in json).toBe(false);
    }
    const b = ActorRef.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects invalid side", () => {
    expect(() =>
      ActorRef.fromJson({ id: "r", kind: "actor_ref", side: "ghost" }),
    ).toThrow(DomainParseError);
  });
});

// mission_ref / value_ref / identity_ref retired 2026-06-20 (D-2026-06-20-G).

describe("Service.fromJson + toJson round-trip (5-field model, D-2026-06-20-F)", () => {
  it("populates defaults", () => {
    const s = Service.fromJson({ id: "svc-1", kind: "service" });
    expect(s.kind).toBe("service");
    expect(s.problem).toBe("");
    expect(s.value_created).toBe("");
    expect(s.ref_actor_ids).toEqual([]);
    expect(s.ref_value_ids).toEqual([]);
    expect(s.ref_identity_ids).toEqual([]);
  });

  it("preserves the 2 typed fields + 3 ref arrays and round-trips", () => {
    const a = Service.fromJson({
      id: "svc-1",
      kind: "service",
      label: "Sign-up",
      problem: "가입이 너무 번거롭다",
      value_created: "빠른 접근권",
      ref_actor_ids: ["a1", "a2"],
      ref_value_ids: ["cv1"],
      ref_identity_ids: ["id1"],
    });
    const b = Service.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("drops legacy 9-field content (discard, no migration)", () => {
    const s = Service.fromJson({
      id: "x",
      kind: "service",
      target_side: "user",
      what: "legacy",
      scope: "legacy",
    });
    expect(s.toJson()).not.toHaveProperty("target_side");
    expect(s.toJson()).not.toHaveProperty("what");
  });

  it("rejects a non-array ref field", () => {
    expect(() =>
      Service.fromJson({ id: "x", kind: "service", ref_actor_ids: "a1" }),
    ).toThrow(DomainParseError);
  });
});

describe("Rule.fromJson + toJson round-trip", () => {
  it("populates defaults including empty actor_permissions", () => {
    const r = Rule.fromJson({ id: "r1", kind: "rule" });
    expect(r.actor_permissions).toEqual({});
  });

  it("preserves typed fields including permissions map", () => {
    const a = Rule.fromJson({
      id: "r1",
      kind: "rule",
      policy: "GDPR opt-in",
      enforcement: "checkbox + audit",
      actor_permissions: { user: "RUD", admin: "CRUD" },
    });
    const b = Rule.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects non-string permission value", () => {
    expect(() =>
      Rule.fromJson({ id: "r1", kind: "rule", actor_permissions: { user: 42 } }),
    ).toThrow(DomainParseError);
  });
});

// content retired 2026-06-20 (D-2026-06-20-H).

describe("parseEntity → service / rule dispatch", () => {
  it("dispatches each", () => {
    expect(parseEntity({ id: "1", kind: "service" })).toBeInstanceOf(Service);
    expect(parseEntity({ id: "2", kind: "rule" })).toBeInstanceOf(Rule);
  });
});

describe("Actor.fromJson + toJson round-trip", () => {
  // D-2026-06-15-J: actor carries identity only (side + body). motivation
  // / pain moved to actor_ref (per-service stake).
  it("populates defaults (identity only)", () => {
    const a = Actor.fromJson({ id: "a1", kind: "actor" });
    expect(a.kind).toBe("actor");
    expect(a.side).toBeNull();
    expect(a.body).toBe("");
    expect("motivation" in a.toJson()).toBe(false);
    expect("pain" in a.toJson()).toBe(false);
  });

  it("preserves typed fields and round-trips", () => {
    const x = Actor.fromJson({
      id: "a1",
      kind: "actor",
      label: "Operator",
      side: "operator",
      body: "운영자 페르소나",
    });
    const y = Actor.fromJson(x.toJson());
    expect({ ...y }).toEqual({ ...x });
  });

  it("rejects invalid side", () => {
    expect(() => Actor.fromJson({ id: "a1", kind: "actor", side: "bot" })).toThrow(
      DomainParseError,
    );
  });

  it("dispatches via parseEntity", () => {
    expect(parseEntity({ id: "a", kind: "actor" })).toBeInstanceOf(Actor);
  });
});

describe("parseEntity → ref kinds dispatch", () => {
  it("dispatches actor_ref (the only surviving standalone ref) to its class", () => {
    expect(parseEntity({ id: "1", kind: "actor_ref", ref_actor_id: "a1" })).toBeInstanceOf(
      ActorRef,
    );
  });
});

describe("Mission.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const m = Mission.fromJson({ id: "m1", kind: "mission" });
    expect(m.kind).toBe("mission");
    expect(m.statement).toBe("");
    expect(m.body).toBe("");
  });

  it("preserves statement + body and round-trips", () => {
    const a = Mission.fromJson({
      id: "m1",
      kind: "mission",
      statement: "누구나 히어로가 되는 일상을 만든다",
      body: "## 스토리\n…",
    });
    const b = Mission.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("migrates legacy what_we_do → statement, folds why/direction → body", () => {
    const m = Mission.fromJson({
      id: "m1",
      kind: "mission",
      what_we_do: "우리는 매일 …",
      why: "사람들이 …",
      direction: "누구나 … 인 일상으로",
      body: "원래 본문",
    });
    expect(m.statement).toBe("우리는 매일 …");
    expect(m.body).toContain("원래 본문");
    expect(m.body).toContain("사람들이 …");
    expect(m.body).toContain("누구나 … 인 일상으로");
    // legacy fields are gone from the domain object
    expect("what_we_do" in m).toBe(false);
  });

  it("rejects raw with the wrong kind", () => {
    expect(() => Mission.fromJson({ id: "m1", kind: "actor" })).toThrow(DomainParseError);
  });

  it("dispatches via parseEntity", () => {
    const node = parseEntity({ id: "m1", kind: "mission", what_we_do: "x" });
    expect(node).toBeInstanceOf(Mission);
  });
});
