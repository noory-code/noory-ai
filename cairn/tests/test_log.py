"""The append-only log: record decisions, never edit; ``in_force`` is derived."""

from pathlib import Path

from cairn.log import Log


def _log(tmp_path: Path) -> Log:
    return Log(tmp_path / ".noory" / "cairn")


def test_record_allocates_id_and_writes(tmp_path: Path) -> None:
    log = _log(tmp_path)
    dec = log.record("Use Postgres", "## Decision\nPostgres.")
    assert dec.id == "CAIRN-001"
    assert dec.status == "accepted"
    assert log.get("CAIRN-001") == dec


def test_record_increments_and_lists_in_order(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.record("first", "a")
    second = log.record("second", "b")
    assert second.id == "CAIRN-002"
    assert log.list_ids() == ["CAIRN-001", "CAIRN-002"]


def test_record_proposed(tmp_path: Path) -> None:
    dec = _log(tmp_path).record("a draft option", "body", status="proposed")
    assert dec.status == "proposed"


def test_in_force_excludes_superseded(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.record("Postgres", "b")  # CAIRN-001
    log.record("CockroachDB", "b", supersedes="CAIRN-001")  # CAIRN-002
    assert [d.id for d in log.in_force()] == ["CAIRN-002"]


def test_in_force_excludes_proposed(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.record("a draft", "b", status="proposed")
    assert log.in_force() == []


def test_proposed_supersede_does_not_retire_until_accepted(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.record("Postgres", "b")  # CAIRN-001 accepted, in force
    log.record("maybe move", "b", status="proposed", supersedes="CAIRN-001")  # not accepted
    assert [d.id for d in log.in_force()] == ["CAIRN-001"]


def test_list_empty(tmp_path: Path) -> None:
    assert _log(tmp_path).list_ids() == []


def test_in_force_about_filter(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.record("Postgres", "b", about=["ACT-005"])  # CAIRN-001
    log.record("Naming convention", "b", about=["ACT-009"])  # CAIRN-002
    assert [d.id for d in log.in_force(about="ACT-005")] == ["CAIRN-001"]
    assert log.in_force(about="ACT-404") == []


def test_in_force_about_respects_supersession(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.record("Postgres", "b", about=["ACT-005"])  # CAIRN-001
    log.record("Cockroach", "b", about=["ACT-005"], supersedes="CAIRN-001")  # CAIRN-002
    assert [d.id for d in log.in_force(about="ACT-005")] == ["CAIRN-002"]
