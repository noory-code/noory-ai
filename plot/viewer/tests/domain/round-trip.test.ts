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
  Content,
  CoreValue,
  DomainParseError,
  Identity,
  IdentityRef,
  Metric,
  Mission,
  MissionRef,
  parseEntity,
  Project,
  Rule,
  Service,
  Step,
  ValueRef,
} from "../../src/domain";

describe("Metric.fromJson + toJson round-trip", () => {
  it("populates defaults from a minimal raw", () => {
    const m = Metric.fromJson({ id: "m1", kind: "metric" });
    expect(m.id).toBe("m1");
    expect(m.kind).toBe("metric");
    expect(m.target).toBe("");
    expect(m.measurement).toBe("");
    expect(m.label).toBe("");
    expect(m.x).toBe(0);
  });

  it("preserves provided typed fields", () => {
    const m = Metric.fromJson({
      id: "m1",
      kind: "metric",
      label: "Latency",
      target: ">99% under 200ms",
      measurement: "p95 from server timing-API",
    });
    expect(m.label).toBe("Latency");
    expect(m.target).toBe(">99% under 200ms");
    expect(m.measurement).toBe("p95 from server timing-API");
  });

  it("toJson emits kind and the typed fields", () => {
    const m = Metric.fromJson({
      id: "m1",
      kind: "metric",
      target: "x",
      measurement: "y",
    });
    const dumped = m.toJson();
    expect(dumped.kind).toBe("metric");
    expect(dumped.target).toBe("x");
    expect(dumped.measurement).toBe("y");
    expect(dumped.id).toBe("m1");
  });

  it("survives a full fromJson / toJson / fromJson round-trip", () => {
    const raw = {
      id: "m1",
      kind: "metric" as const,
      label: "L",
      x: 10,
      y: 20,
      width: 200,
      height: 90,
      color: "#fef3c7",
      shape: "rounded" as const,
      icon: null,
      parent_id: "svc-1",
      collapsed: false,
      is_root: false,
      details_path: "services/svc-1/m1.md",
      target: "x",
      measurement: "y",
    };
    const a = Metric.fromJson(raw);
    const b = Metric.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects raw with the wrong kind", () => {
    expect(() => Metric.fromJson({ id: "m1", kind: "actor" })).toThrow(DomainParseError);
  });

  it("rejects raw with non-string typed field", () => {
    expect(() => Metric.fromJson({ id: "m1", kind: "metric", target: 42 })).toThrow(
      DomainParseError,
    );
  });

  it("treats a missing typed field as empty string", () => {
    const m = Metric.fromJson({ id: "m1", kind: "metric", target: undefined });
    expect(m.target).toBe("");
  });

  it("instances spread as plain data (React Flow safety)", () => {
    // applyNodeChanges will spread {...node, x: newX} — that must
    // preserve every BaseFields + typed field even though prototype
    // methods (toJson) are lost on the spread copy.
    const m = Metric.fromJson({
      id: "m1",
      kind: "metric",
      target: "x",
      measurement: "y",
    });
    const spread = { ...m };
    expect(spread.id).toBe("m1");
    expect(spread.kind).toBe("metric");
    expect(spread.target).toBe("x");
    expect(spread.measurement).toBe("y");
    // v0.24.15 (D-2026-05-24-A) — default width reduced 140 → 80.
    expect(spread.width).toBe(80);
  });
});

describe("parseEntity → Metric dispatch", () => {
  it("returns a Metric instance for kind=\"metric\"", () => {
    const node = parseEntity({ id: "m1", kind: "metric", target: "x" });
    expect(node).toBeInstanceOf(Metric);
    expect((node as Metric).target).toBe("x");
  });
});

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
    expect(() => Step.fromJson({ id: "s1", kind: "metric" })).toThrow(DomainParseError);
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
    expect(() => CoreValue.fromJson({ id: "cv1", kind: "metric" })).toThrow(DomainParseError);
  });
});

describe("Identity.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const id = Identity.fromJson({ id: "id1", kind: "identity" });
    expect(id.kind).toBe("identity");
    expect(id.description).toBe("");
    expect(id.do).toBe("");
    expect(id.dont).toBe("");
  });

  it("preserves typed fields and round-trips", () => {
    const a = Identity.fromJson({
      id: "id1",
      kind: "identity",
      label: "Voice",
      description: "따뜻하고 진솔하게",
      do: "이름을 부른다",
      dont: "공지글 같은 말투로",
    });
    const b = Identity.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
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

describe("ActorRef.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const r = ActorRef.fromJson({ id: "ref-1", kind: "actor_ref" });
    expect(r.kind).toBe("actor_ref");
    expect(r.ref_actor_id).toBeNull();
    expect(r.gives).toBe("");
    expect(r.receives).toBe("");
    expect(r.side).toBeNull();
  });

  it("preserves ref + gives/receives/side and round-trips", () => {
    const a = ActorRef.fromJson({
      id: "ref-1",
      kind: "actor_ref",
      ref_actor_id: "operator",
      gives: "moderation",
      receives: "reputation",
      side: "operator",
    });
    const b = ActorRef.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects invalid side", () => {
    expect(() =>
      ActorRef.fromJson({ id: "r", kind: "actor_ref", side: "ghost" }),
    ).toThrow(DomainParseError);
  });
});

describe("Foundation refs (Mission/Value/Identity) round-trip", () => {
  it("MissionRef preserves ref_mission_id", () => {
    const m = MissionRef.fromJson({
      id: "mref-1",
      kind: "mission_ref",
      ref_mission_id: "mission-1",
    });
    expect(m.kind).toBe("mission_ref");
    expect(m.ref_mission_id).toBe("mission-1");
    expect(MissionRef.fromJson(m.toJson())).toEqual(m);
  });

  it("ValueRef preserves ref_value_id", () => {
    const v = ValueRef.fromJson({ id: "vref-1", kind: "value_ref", ref_value_id: "cv-1" });
    expect(v.ref_value_id).toBe("cv-1");
  });

  it("IdentityRef preserves ref_identity_id", () => {
    const i = IdentityRef.fromJson({
      id: "iref-1",
      kind: "identity_ref",
      ref_identity_id: "id-1",
    });
    expect(i.ref_identity_id).toBe("id-1");
  });
});

describe("Service.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const s = Service.fromJson({ id: "svc-1", kind: "service" });
    expect(s.kind).toBe("service");
    expect(s.target_side).toBeNull();
    expect(s.what).toBe("");
  });

  it("preserves all 6 typed fields + do/dont and round-trips", () => {
    const a = Service.fromJson({
      id: "svc-1",
      kind: "service",
      label: "Sign-up",
      target_side: "user",
      what: "신규 가입",
      value_created: "접근권",
      scope: "이메일/패스워드",
      trigger: "/signup 진입",
      how: "이메일 + 비번",
      outcome: "계정 생성",
      do: "진행 표시",
      dont: "불필요 필드 묻기",
    });
    const b = Service.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });

  it("rejects invalid target_side", () => {
    expect(() =>
      Service.fromJson({ id: "x", kind: "service", target_side: "bot" }),
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

describe("Content.fromJson + toJson round-trip", () => {
  it("populates defaults with null actor refs", () => {
    const c = Content.fromJson({ id: "c1", kind: "content" });
    expect(c.format).toBe("");
    expect(c.producer_actor_id).toBeNull();
    expect(c.consumer_actor_id).toBeNull();
  });

  it("preserves typed fields and round-trips", () => {
    const a = Content.fromJson({
      id: "c1",
      kind: "content",
      format: "application/json",
      producer_actor_id: "checkout",
      consumer_actor_id: "user",
    });
    const b = Content.fromJson(a.toJson());
    expect({ ...b }).toEqual({ ...a });
  });
});

describe("parseEntity → service / rule / content dispatch", () => {
  it("dispatches each", () => {
    expect(parseEntity({ id: "1", kind: "service" })).toBeInstanceOf(Service);
    expect(parseEntity({ id: "2", kind: "rule" })).toBeInstanceOf(Rule);
    expect(parseEntity({ id: "3", kind: "content" })).toBeInstanceOf(Content);
  });
});

describe("Actor.fromJson + toJson round-trip", () => {
  it("populates defaults", () => {
    const a = Actor.fromJson({ id: "a1", kind: "actor" });
    expect(a.kind).toBe("actor");
    expect(a.motivation).toBe("");
    expect(a.pain).toBe("");
    expect(a.side).toBeNull();
  });

  it("preserves typed fields and round-trips", () => {
    const x = Actor.fromJson({
      id: "a1",
      kind: "actor",
      label: "Operator",
      motivation: "운영 부담",
      pain: "탭이 너무 많다",
      side: "operator",
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
  it("dispatches each ref kind to its class", () => {
    expect(parseEntity({ id: "1", kind: "actor_ref" })).toBeInstanceOf(ActorRef);
    expect(parseEntity({ id: "2", kind: "mission_ref" })).toBeInstanceOf(MissionRef);
    expect(parseEntity({ id: "3", kind: "value_ref" })).toBeInstanceOf(ValueRef);
    expect(parseEntity({ id: "4", kind: "identity_ref" })).toBeInstanceOf(IdentityRef);
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
