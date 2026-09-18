"""Rebuilding a lost registry from the XML files that were uploaded: the restored registry must
carry the same chains, keys and content hashes as the original, so the next workbook plans
exactly as it would have (unchanged rows stay unchanged, corrections reference the right
DocRefIds), and never reports an account twice."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from aeoi import cli
from aeoi.crs import build, restore, template, workflow
from aeoi.crs.example import sample_message
from aeoi.registry import Registry, content_hash, identity


@pytest.fixture
def reg(tmp_path):
    with Registry(tmp_path / "institut.sqlite") as r:
        yield r


@pytest.fixture
def fresh(tmp_path):
    with Registry(tmp_path / "restored.sqlite") as r:
        yield r


def _accept(reg, ref):
    workflow.record_outcome(reg, f"MessageRefId {ref}\nStatus: accepted\n", message_ref_id=ref)


def _files(outs) -> list[tuple[str, bytes]]:
    return [(o.xml_name, o.result.xml.encode("utf-8")) for o in outs]


def _heads(reg, *, year=2026, test=False):
    return {
        h.account_key: (h.doc_ref_id, h.content_sha256, h.version, h.message_status)
        for h in reg.chain_heads(year=year, test=test)
    }


def test_round_trip_new_and_correction(reg, fresh):
    """Original registry: new message, accepted; correction + new account, accepted. The registry
    restored from the two XML files (keys from the workbook) has identical chain heads."""
    msg = sample_message()
    t0 = dt.datetime(2026, 3, 1, 10, 0, tzinfo=dt.UTC)
    first = workflow.build(msg, "3.0", reg, test=False, now=t0)
    _accept(reg, first[0].result.message_ref_id)
    changed = msg.model_copy(deep=True)
    changed.accounts[0].balance += 1
    changed.accounts.append(
        changed.accounts[1].model_copy(
            update={"key": "A3", "doc_ref_id": None, "account_number": "CH5604835012345678009"}
        )
    )
    second = workflow.build(changed, "3.0", reg, test=False, cancel=["A2"], now=t0.replace(day=2))
    assert [o.kind for o in second] == ["correction", "new"]
    for o in second:
        _accept(reg, o.result.message_ref_id)

    # files given in the wrong order: the Timestamp orders them
    files = list(reversed(_files(first + second)))
    report = restore.restore(fresh, files, workbook=changed)
    assert not report.skipped and [f.kind for f in report.restored] == ["new", "new", "correction"]
    assert report.accounts == 2 + 1 + 2
    assert [f.keys_from_workbook for f in report.restored] == [2, 1, 0]  # corrections: chain
    assert all(f.status == "accepted" and not f.notes for f in report.restored)
    assert _heads(fresh) == _heads(reg)
    assert {k for k in _heads(fresh)} == {"A1", "A3"}  # A2 was cancelled
    assert fresh.fi_doc_ref_id(year=2026, test=False) == reg.fi_doc_ref_id(year=2026, test=False)
    for m in fresh.messages():
        assert m["status"] == "accepted" and m["status_source"].startswith("restored from ")
    assert [m["created_at"] for m in fresh.messages()] == [
        "2026-03-01T10:00:00+00:00", "2026-03-02T10:00:00+00:00", "2026-03-02T10:00:00+00:00"
    ]  # fmt: skip

    # the next workbook plans exactly as against the original
    same = changed.model_copy(deep=True)
    same.accounts = [a for a in same.accounts if a.key != "A2"]
    for r in (reg, fresh):
        intent = workflow.plan(same, "3.0", r, test=False)
        assert intent.unchanged == ["A1", "A3"] and intent.messages == [], intent.problems
    same.accounts[0].balance += 5  # A1 again: the target is the corrected record, not the first
    outs = workflow.build(same, "3.0", fresh, test=False)
    assert [o.kind for o in outs] == ["correction"]
    plan = outs[0].result.records
    assert [(p.key, p.doc_type_indic, p.corr_doc_ref_id) for p in plan] == [
        ("A1", "OECD2", _heads(reg)["A1"][0])
    ]
    assert _heads(reg)["A1"][0] != first[0].result.doc_ref_ids["A1"]


def test_amounts_hash_alike_however_they_were_typed():
    """1500, 1500.0 and 1500.00 are one balance; a restored record equals its workbook row."""
    a = sample_message().accounts[0]
    variants = [
        a.model_copy(update={"balance": a.balance.__class__(s)}) for s in ("0", "0.0", "0.00")
    ]
    assert len({content_hash(v, "3.0") for v in variants}) == 1


def test_keys_without_workbook_and_the_duplicate_guard(reg, fresh):
    msg = sample_message()
    outs = workflow.build(msg, "3.0", reg, test=False)
    _accept(reg, outs[0].result.message_ref_id)
    report = restore.restore(fresh, _files(outs))
    f = report.restored[0]
    assert f.keys_from_number == 2 and set(f.keys.values()) == {
        a.account_number for a in msg.accounts
    }
    # the workbook still says A1/A2: the plan refuses to report the accounts a second time
    intent = workflow.plan(msg, "3.0", fresh, test=False)
    assert intent.blocked == ["A1", "A2"] and not intent.new_keys
    assert "under key 'CH9300762011623852957'" in intent.problems[0]
    with pytest.raises(workflow.WorkflowError):
        workflow.build(msg, "3.0", fresh, test=False)
    # keys aligned in the workbook -> unchanged
    aligned = msg.model_copy(deep=True)
    for a in aligned.accounts:
        a.key = a.account_number
    intent = workflow.plan(aligned, "3.0", fresh, test=False)
    assert intent.unchanged == [a.account_number for a in msg.accounts] and not intent.blocked
    # a really new account (other number) is still new
    extra = msg.model_copy(deep=True)
    extra.accounts = [extra.accounts[0].model_copy(update={"key": "A9", "account_number": "X1"})]
    intent = workflow.plan(extra, "3.0", fresh, test=False)
    assert intent.new_keys == ["A9"] and not intent.blocked


def test_renamed_key_is_blocked_even_without_restore(reg):
    """The guard is general: renaming A1 to K1 in the workbook must not double the record."""
    msg = sample_message()
    outs = workflow.build(msg, "3.0", reg, test=True)
    _accept(reg, outs[0].result.message_ref_id)
    renamed = msg.model_copy(deep=True)
    renamed.accounts[0].key = "K1"
    intent = workflow.plan(renamed, "3.0", reg, test=True)
    assert intent.blocked == ["K1"] and intent.unchanged == ["A2"]
    assert "'A1'" in intent.problems[0]
    # the same holder with a changed account number is a different report: new, not blocked
    moved = msg.model_copy(deep=True)
    moved.accounts[0].key, moved.accounts[0].account_number = "K1", "CH0000000000000000000"
    assert workflow.plan(moved, "3.0", reg, test=True).new_keys == ["K1"]


def test_joint_account_fallback_keys(fresh):
    """Two holders of one account number: both records get distinct keys from the number."""
    msg = sample_message()
    second = msg.accounts[0].model_copy(deep=True, update={"key": "A2j", "doc_ref_id": None})
    second.holder_person.last_name = "Other"
    msg.accounts = [msg.accounts[0], second]
    xml = build.build(msg, "3.0").xml
    report = restore.restore(fresh, [("joint.xml", xml.encode())])
    keys = list(report.restored[0].keys.values())
    number = msg.accounts[0].account_number
    assert keys == [number, f"{number}/Other {second.holder_person.first_name}"]
    assert identity(msg.accounts[0]) != identity(second)


def test_test_files_wegleitung_header_and_20(fresh):
    msg = sample_message()
    t = build.build(msg, "3.0", test=True, header="wegleitung").xml
    p2 = build.build(msg, "2.0").xml
    report = restore.restore(fresh, [("Test-a.xml", t.encode()), ("b.xml", p2.encode())])
    by_name = {f.name: f for f in report.restored}
    assert by_name["Test-a.xml"].test and by_name["Test-a.xml"].version == "3.0"
    assert [str(n) for n in by_name["Test-a.xml"].notes] == [
        "header as in Wegleitung 5.3.1 (v2 namespace with version 3.0); stored as a 3.0 message"
    ]
    assert not by_name["b.xml"].test and by_name["b.xml"].version == "2.0"
    heads = fresh.chain_heads(year=2026, test=False)
    assert {h.version for h in heads} == {"2.0"}  # the hash is a 2.0 projection
    assert {r.doc_type_indic for r in fresh.chain_heads(year=2026, test=True)} == {"OECD1"}
    # the 3.0 workbook against the 2.0 record: unchanged (V2 projection), not "changed"
    aligned = msg.model_copy(deep=True)
    for a in aligned.accounts:
        a.key = a.account_number
    assert workflow.plan(aligned, "3.0", fresh, test=False).unchanged == [
        a.account_number for a in msg.accounts
    ]


def test_skips_duplicates_junk_and_mixed_files(fresh, tmp_path):
    msg = sample_message()
    xml = build.build(msg, "3.0").xml
    junk = tmp_path / "notes.xml"
    junk.write_text("<hello/>", encoding="utf-8")
    mixed = xml.replace(
        "<stf:DocTypeIndic>OECD1</stf:DocTypeIndic>",
        "<stf:DocTypeIndic>OECD11</stf:DocTypeIndic>",
        1,
    )
    report = restore.restore(
        fresh, [("a.xml", xml.encode()), ("z-again.xml", xml.encode()), ("m.xml", mixed.encode())]
    )
    assert [f.name for f in report.restored] == ["a.xml"]
    assert [(n, r.id) for n, r in report.skipped] == [
        ("m.xml", "restore_mixed_test"), ("z-again.xml", "restore_already")
    ]  # fmt: skip
    report = restore.restore(fresh, [junk])
    assert report.skipped[0][0] == "notes.xml" and report.skipped[0][1].id == "restore_not_crs"
    # a file that reuses a DocRefId under another MessageRefId cannot be right (80000)
    clash = xml.replace(msg.message_ref_id or "CH2026CH", "CH2026CHother-ref", 1)
    ref = build.build(msg, "3.0").message_ref_id  # any unused MessageRefId
    clash = xml.replace(restore.read_xml.parse(xml).message.message_ref_id, ref)
    report = restore.restore(fresh, [("clash.xml", clash.encode())])
    assert report.skipped and report.skipped[0][1].id == "reg_docref_used"
    with pytest.raises(restore.RegistryError, match="accepted, submitted"):
        restore.restore(fresh, [], status="rejected")


def test_correction_without_its_target_starts_a_chain(reg, fresh):
    msg = sample_message()
    first = workflow.build(msg, "3.0", reg, test=False)
    _accept(reg, first[0].result.message_ref_id)
    changed = msg.model_copy(deep=True)
    changed.accounts[0].balance += 1
    corr = workflow.build(changed, "3.0", reg, test=False)
    report = restore.restore(fresh, _files(corr), workbook=changed)
    f = report.restored[0]
    assert f.kind == "correction" and f.notes and f.notes[0].id == "restore_target_missing"
    # the corrected record is the valid head under the workbook key, and the FI DocRefId
    # (an OECD0 in the file) is known for the next resend
    assert list(_heads(fresh)) == ["A1"]
    assert fresh.fi_doc_ref_id(year=2026, test=False) == reg.fi_doc_ref_id(year=2026, test=False)
    assert workflow.plan(changed, "3.0", fresh, test=False).unchanged == ["A1"]


def test_submitted_status_blocks_corrections_until_recorded(fresh):
    msg = sample_message()
    xml = build.build(msg, "3.0").xml
    report = restore.restore(fresh, [("a.xml", xml.encode())], status="submitted", workbook=msg)
    ref = report.restored[0].message_ref_id
    assert workflow.registry_view(fresh)["pending"] == [ref]
    intent = workflow.plan(msg, "3.0", fresh, test=False)
    assert intent.blocked == ["A1", "A2"]
    _accept(fresh, ref)
    assert workflow.plan(msg, "3.0", fresh, test=False).unchanged == ["A1", "A2"]


def test_cli_restore(tmp_path, capsys):
    msg = sample_message()
    xlsx = tmp_path / "book.xlsx"
    template.write_message(msg, xlsx)
    xml = tmp_path / "CRS-2026-abc.xml"
    xml.write_text(build.build(msg, "3.0").xml, encoding="utf-8")
    regp = tmp_path / "restored.sqlite"
    rc = cli.main(
        ["crs", "restore", "--registry", str(regp), str(xml), "--input", str(xlsx), "--lang", "de"]
    )
    out = capsys.readouterr().out
    assert rc == 0 and '"keys_from_workbook": 2' in out and '"status": "accepted"' in out
    with Registry(regp) as r:
        assert workflow.plan(msg, "3.0", r, test=False).unchanged == ["A1", "A2"]
    # once more: skipped as already there, exit code 1 tells scripts
    rc = cli.main(["crs", "restore", "--registry", str(regp), str(xml)])
    assert rc == 1 and "already in the registry" in capsys.readouterr().out
    assert cli.main(["crs", "restore", "--registry", str(regp), str(Path(xml))]) == 1
