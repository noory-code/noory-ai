import importlib.util
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[1]
STAGE = HOOKS.parent
SPEC = importlib.util.spec_from_file_location("stage_topology", HOOKS / "stage_topology.py")
stage_topology = importlib.util.module_from_spec(SPEC)
sys.modules["stage_topology"] = stage_topology
assert SPEC.loader is not None
SPEC.loader.exec_module(stage_topology)

PATHS_SPEC = importlib.util.spec_from_file_location("stage_paths", HOOKS / "stage_paths.py")
stage_paths = importlib.util.module_from_spec(PATHS_SPEC)
sys.modules["stage_paths"] = stage_paths
assert PATHS_SPEC.loader is not None
PATHS_SPEC.loader.exec_module(stage_paths)


class StageTopologyTests(unittest.TestCase):
    def test_cross_family_contract(self):
        self.assertEqual(4, stage_topology.SCHEMA_VERSION)
        self.assertEqual(("planned", "current", "official"), stage_topology.LIFECYCLE_STATES)
        self.assertTrue(stage_topology.SINGLE_CLASSIFICATION)
        self.assertEqual("official", stage_topology.OFFICIAL_ROOT)
        self.assertTrue(stage_topology.MAINTENANCE_MARKER.startswith(".runtime/"))

    def test_every_declared_zone_is_resolvable(self):
        self.assertEqual(
            {
                "canon",
                "model",
                "decisions",
                "work",
                "state",
                "proposals",
                "roadmap",
                "operations",
            },
            set(stage_topology.FAMILIES),
        )
        for family_name, family in stage_topology.FAMILIES.items():
            self.assertIs(family, stage_topology.get_family(family_name))
            for zone in family.zones:
                self.assertIs(zone, stage_topology.get_zone(family_name, zone.name))
                resolved = stage_topology.resolve_zone(zone.canonical_path + "/record.md")
                self.assertIsNotNone(resolved)
                assert resolved is not None
                self.assertEqual(family_name, resolved[0])
                self.assertIs(zone, resolved[1])

    def test_unknown_family_zone_and_path_fail_fast(self):
        with self.assertRaises(ValueError):
            stage_topology.get_family("missing")
        with self.assertRaises(ValueError):
            stage_topology.get_zone("work", "missing")
        self.assertIsNone(stage_topology.resolve_zone("settings.json"))
        with self.assertRaises(ValueError):
            stage_topology.resolve_lifecycle("settings.json")

    def test_static_and_decision_derived_lifecycle_resolution(self):
        self.assertEqual(
            "current",
            stage_topology.resolve_lifecycle(".stage/work/current/W-00000001.md", status="active"),
        )
        with self.assertRaises(ValueError):
            stage_topology.resolve_lifecycle(
                "work/current/W-00000001.md", status="captured"
            )
        self.assertEqual(
            "planned",
            stage_topology.resolve_lifecycle(
                "roadmap/milestones/M-00000001.md", decision_state="planned"
            ),
        )
        with self.assertRaises(ValueError):
            stage_topology.resolve_lifecycle("roadmap/themes/TH-00000001.md")

    def test_card_location_resolver_handles_rejected_ambiguity(self):
        self.assertEqual("work/planned", stage_topology.card_location_for_status("ready"))
        self.assertEqual("work/current", stage_topology.card_location_for_status("review"))
        self.assertEqual(
            "official/work/archive/items",
            stage_topology.card_location_for_status("archived"),
        )
        with self.assertRaises(ValueError):
            stage_topology.card_location_for_status("rejected")
        self.assertEqual(
            "work/planned",
            stage_topology.card_location_for_status("rejected", lifecycle="planned"),
        )
        with self.assertRaises(ValueError):
            stage_topology.card_location_for_status("unknown")

    def test_card_location_resolver_builds_epic_story_action_hierarchy(self):
        self.assertEqual(
            "work/current/E-01-driver/_epic.md",
            stage_topology.card_location_for_status("active", epic="E-01-driver"),
        )
        self.assertEqual(
            "work/current/E-01-driver/S-01-review/_story.md",
            stage_topology.card_location_for_status(
                "active",
                epic="E-01-driver",
                story="S-01-review",
            ),
        )
        self.assertEqual(
            "work/current/E-01-driver/S-01-review/A-01-driver.md",
            stage_topology.card_location_for_status(
                "active",
                epic="E-01-driver",
                story="S-01-review",
                action="A-01-driver.md",
            ),
        )
        self.assertEqual(
            "work/planned/S-05-decision/_story.md",
            stage_topology.card_location_for_status(
                "captured",
                story="S-05-decision",
            ),
        )

    def test_card_location_resolver_rejects_invalid_hierarchy(self):
        with self.assertRaises(ValueError):
            stage_topology.card_location_for_status("active", action="A-01.md")
        with self.assertRaises(ValueError):
            stage_topology.card_location_for_status(
                "active",
                epic="E-01",
                action="A-01.md",
            )
        with self.assertRaises(ValueError):
            stage_topology.card_location_for_status(
                "active",
                story="../S-01",
            )

    def test_top_level_card_location_is_the_lifecycle_move_unit(self):
        self.assertEqual(
            "work/current/E-01-driver",
            stage_topology.top_level_card_location_for_status(
                "active",
                epic="E-01-driver",
                story="S-01-review",
                action="A-01-driver.md",
            ),
        )
        self.assertEqual(
            "official/work/archive/items/S-05-decision",
            stage_topology.top_level_card_location_for_status(
                "archived",
                story="S-05-decision",
                action="A-01-decision.md",
            ),
        )

    def test_retrospective_locations(self):
        self.assertEqual(
            ("work/retrospectives", "official/work/archive/retrospectives"),
            stage_topology.retrospective_locations(),
        )
        self.assertEqual(
            (
                "work/retrospectives/R-00000001.md",
                "official/work/archive/retrospectives/R-00000001.md",
            ),
            stage_topology.retrospective_locations("R-00000001"),
        )
        with self.assertRaises(ValueError):
            stage_topology.retrospective_locations("W-00000001")

    def test_reference_path_calculation_does_not_read_the_process_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            action = cwd / "work/current/E-01-epic/S-01-story/A-01-action.md"
            retrospective = cwd / "work/retrospectives/S-01-story/_story.md"
            action.parent.mkdir(parents=True)
            retrospective.parent.mkdir(parents=True)
            action.write_text("---\nid: W-00000001\n---\n", encoding="utf-8")
            retrospective.write_text("---\nid: R-00000001\n---\n", encoding="utf-8")

            original_cwd = Path.cwd()
            os.chdir(cwd)
            try:
                self.assertEqual(
                    "work/current/W-00000001.md",
                    stage_topology.resolve_artifact_reference(
                        "W-00000001"
                    ).candidate_paths[1],
                )
                self.assertEqual(
                    "work/retrospectives/R-00000001.md",
                    stage_topology.retrospective_locations("R-00000001")[0],
                )
            finally:
                os.chdir(original_cwd)

    def test_scan_roots_are_derived_by_purpose(self):
        records = stage_topology.scan_roots("records")
        audit = stage_topology.scan_roots("audit")
        context = stage_topology.scan_roots("context")
        self.assertIn("work/current", records)
        self.assertIn("work/active.md", audit)
        self.assertIn("state/questions", context)
        self.assertNotIn("official/canon/principles", context)
        with self.assertRaises(ValueError):
            stage_topology.scan_roots("migration")

    def test_prefixes_parse_legacy_widths_and_use_per_type_counters(self):
        policy, number = stage_topology.parse_artifact_id("W-123")
        self.assertEqual("W", policy.prefix)
        self.assertEqual(123, number)
        # Each artifact type counts its own sequence: a question ignores sibling
        # observations, and a milestone ignores sibling themes (DE-00000012).
        self.assertEqual(
            "Q-00000004",
            stage_topology.next_artifact_id("Q", ["O-00000009", "Q-003", "W-99999999"]),
        )
        self.assertEqual(
            "M-00000003",
            stage_topology.next_artifact_id("M", ["TH-00000007", "M-00000002"]),
        )
        with self.assertRaises(ValueError):
            stage_topology.parse_artifact_id("W-12")
        with self.assertRaises(ValueError):
            stage_topology.next_artifact_id("D", [])

    def test_decision_references_keep_de_identity_and_resolve_legacy_d(self):
        current = stage_topology.resolve_artifact_reference("DE-00000009")
        self.assertFalse(current.legacy)
        self.assertEqual(
            (
                "decisions/pending/DE-00000009.md",
                "official/decisions/records/DE-00000009.md",
            ),
            current.candidate_paths,
        )
        legacy = stage_topology.resolve_artifact_reference("D-00000009")
        self.assertTrue(legacy.legacy)
        self.assertEqual(
            ("official/decisions/records/D-00000009.md",), legacy.candidate_paths
        )

    def test_relocation_map_is_bijective_and_uses_longest_match(self):
        mapping = stage_topology.V3_TO_V4_RELOCATIONS
        self.assertEqual(len(mapping), len(set(mapping.values())))
        self.assertEqual("official", mapping["past"])
        for origin, destination in mapping.items():
            self.assertTrue(stage_topology.is_legacy_path(origin))
            self.assertEqual(destination, stage_topology.relocate_v3_path(origin))
        self.assertEqual(
            ".stage/work/planned/W-00000001.md",
            stage_topology.relocate_v3_path(
                ".stage/future/backlog/items/W-00000001.md"
            ),
        )
        self.assertEqual("settings.json", stage_topology.relocate_v3_path("settings.json"))
        for root in ("past", "present", "future"):
            self.assertTrue(stage_topology.is_legacy_path(f".stage/{root}/recreated.md"))
        self.assertFalse(stage_topology.is_legacy_path("official/canon/principles.md"))
        self.assertEqual(
            ("work/current/W-00000001.md",),
            stage_topology.legacy_replacement_paths(
                ".stage/present/work/items/W-00000001.md"
            ),
        )
        self.assertEqual(
            ("decisions", "state", "work"),
            stage_topology.legacy_replacement_paths(".stage/present/recreated.md"),
        )

    def test_authorization_zone_matches_stage_paths(self):
        self.assertEqual(
            f".stage/{stage_topology.OFFICIAL_ROOT}", stage_paths.STAGE_OFFICIAL_ROOT
        )
        self.assertEqual(
            ".stage/official/work/archive", stage_paths.STAGE_OFFICIAL_ARCHIVE_ROOT
        )
        self.assertTrue(
            stage_paths.path_targets_stage_official(".stage/official/canon/principles.md")
        )
        self.assertTrue(
            stage_paths.path_targets_stage_official(
                "/workspace/.stage/official/canon/principles.md"
            )
        )
        self.assertTrue(
            stage_paths.path_targets_stage_official_archive(
                ".stage/official/work/archive/items/W-00000001.md"
            )
        )
        self.assertFalse(
            stage_paths.path_targets_stage_official(".stage/officially/canon/principles.md")
        )
        self.assertFalse(stage_paths.path_targets_stage_official(".stage/past/canon/principles.md"))

    def test_legacy_topology_literals_do_not_exceed_adoption_baseline(self):
        # DE-00000010: these schema-v3 consumers are rewired by C4-C5 and C7.
        # This is a ratchet, not a permanent exemption: counts may only fall, no
        # new production module may acquire a legacy topology literal, and C7
        # removes the baseline when adoption reaches zero.
        baseline = {
            "hooks/stage_context.py": 13,
            "hooks/stage_guard.py": 1,
            "hooks/stage_runtime.py": 3,
            "hooks/stage_work.py": 9,
            "scripts/audit_stage.py": 39,
            "scripts/migrate_stage.py": 3,
            "scripts/promote_intent.py": 1,
            "scripts/stage_records.py": 3,
            "scripts/start_work.py": 6,
            "skills/stage-archive/archive_work.py": 1,
            "skills/stage-work/register_work.py": 6,
        }
        legacy_literal = re.compile(r"(?:past|present|future)/")
        actual = {}
        for source_root in (STAGE / "hooks", STAGE / "scripts", STAGE / "skills"):
            for path in source_root.rglob("*.py"):
                if "tests" in path.parts or path.name in {
                    "stage_topology.py",
                    "stage_paths.py",
                }:
                    continue
                count = len(legacy_literal.findall(path.read_text(encoding="utf-8")))
                if count:
                    actual[path.relative_to(STAGE).as_posix()] = count

        unexpected = sorted(set(actual) - set(baseline))
        excess = {
            path: (count, baseline[path])
            for path, count in actual.items()
            if path in baseline and count > baseline[path]
        }
        self.assertEqual([], unexpected, f"new legacy-topology consumers: {unexpected}")
        self.assertEqual({}, excess, f"legacy-topology literal counts increased: {excess}")
        self.assertLessEqual(sum(actual.values()), 85)


if __name__ == "__main__":
    unittest.main()
