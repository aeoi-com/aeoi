"""Submission workflow on top of the registry: new messages, corrections, deletions, outcomes.

Follows Wegleitung Ziffer 6:

- new message (CRS701): every account is OECD1 with a fresh DocRefId; the ReportingFI is OECD1
  the first time and OECD0 (resend, same DocRefId) afterwards (6.4.6, 98102);
- correction message (CRS702): only accounts whose content changed (OECD2) or that are to be
  deleted (OECD3); each carries a fresh DocRefId and the CorrDocRefId of the last valid link of
  its chain (6.3.3); unchanged accounts are left out; new accounts are refused (they belong in
  a new CRS701 message); the ReportingFI is resent (OECD0);
- nil report (CRS703): refused while valid records exist for the year (98009);
- outcome: the registry marks the message accepted/rejected; a rejected correction frees its
  targets so the chain stays at the previous link.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from aeoi.crs import build as builder
from aeoi.crs import model, xsd
from aeoi.crs.build import BuildResult, FiPlan, RecordPlan
from aeoi.crs.model import Account, Message, Version
from aeoi.estv import ids, status
from aeoi.registry import Registry, RegistryError, content_hash


@dataclass
class Plan:
    records: list[RecordPlan] = field(default_factory=list)
    accounts: list[Account] = field(default_factory=list)
    skipped_unchanged: list[str] = field(default_factory=list)
    fi_plan: FiPlan | None = None


def _check(msg: Message, version: Version, *, correction: bool) -> None:
    report = model.check_message(msg, version, correction=correction)
    errors = [p for p in report.problems if p.rule != "info"]
    if errors:
        text = "; ".join(f"{p.where}: {p.message} [{p.rule}]" for p in errors)
        raise RegistryError(f"message has {len(errors)} problem(s): {text}")


def _fi_plan(reg: Registry, *, year: int, test: bool) -> FiPlan:
    existing = reg.fi_doc_ref_id(year=year, test=test)
    if existing:
        return FiPlan(existing, resend=True)
    return FiPlan(ids.doc_ref_id(year))


def _finish(
    reg: Registry, msg: Message, version: Version, result: BuildResult, *, test: bool,
    out_path: str | Path | None,
) -> BuildResult:  # fmt: skip
    errors = xsd.validate(result.xml, version)
    if errors:
        raise RegistryError("built XML is not valid against the OECD schema: " + "; ".join(errors))
    if out_path is not None:
        Path(out_path).write_text(result.xml, encoding="utf-8")
    by_key = {a.key: a for a in msg.accounts}
    assert result.fi_plan is not None
    reg.register_message(
        message_ref_id=result.message_ref_id,
        reporting_year=msg.reporting_year,
        version=version,
        message_type_indic=msg.message_type_indic,
        test=test,
        xml=result.xml,
        xml_path=str(out_path) if out_path else None,
        fi_doc_ref_id=result.fi_plan.doc_ref_id,
        fi_resend=result.fi_plan.resend,
        records=[
            (p.doc_ref_id, by_key[p.key], p.doc_type_indic, p.corr_doc_ref_id)
            for p in result.records
        ],
    )
    return result


def build_new(
    msg: Message,
    version: Version,
    reg: Registry,
    *,
    test: bool = False,
    out_path: str | Path | None = None,
    now: dt.datetime | None = None,
) -> BuildResult:
    """CRS701 (or CRS703 nil report) with the registry: fresh identifiers, FI resend, 98009."""
    _check(msg, version, correction=False)
    year = msg.reporting_year
    if msg.message_type_indic == "CRS703" and reg.has_valid_records(year=year, test=test):
        raise RegistryError(
            f"nil report refused: valid records exist for {year}; delete them first (98009)"
        )
    if msg.message_ref_id:
        reg.assert_message_ref_id_unused(msg.message_ref_id)
    records = []
    for acc in msg.accounts:
        ref = acc.doc_ref_id or ids.doc_ref_id(year)
        reg.assert_doc_ref_id_unused(ref)
        if reg.chain_head(acc.key, year=year, test=test) is not None:
            raise RegistryError(
                f"account {acc.key!r} already has a valid record for {year}: use a correction "
                "(OECD2) or a deletion (OECD3), not a new record (6.1)"
            )
        records.append(RecordPlan(acc.key, ref, "OECD1"))
    result = builder.build(
        msg, version, test=test, now=now, records=records,
        fi_plan=_fi_plan(reg, year=year, test=test),
    )  # fmt: skip
    return _finish(reg, msg, version, result, test=test, out_path=out_path)


def plan_correction(
    msg: Message, reg: Registry, *, test: bool, cancel: list[str] | None = None
) -> Plan:
    """Decide OECD2 / OECD3 per account from the workbook and the registry."""
    year = msg.reporting_year
    cancel = list(cancel or [])
    plan = Plan(fi_plan=_fi_plan(reg, year=year, test=test))
    keys_in_msg = {a.key for a in msg.accounts}
    for acc in msg.accounts:
        head = reg.correction_target(acc.key, year=year, test=test)
        if acc.key in cancel:
            plan.records.append(RecordPlan(acc.key, ids.doc_ref_id(year), "OECD3", head.doc_ref_id))
            plan.accounts.append(acc)
        elif content_hash(acc) == head.content_sha256:
            plan.skipped_unchanged.append(acc.key)
        else:
            plan.records.append(RecordPlan(acc.key, ids.doc_ref_id(year), "OECD2", head.doc_ref_id))
            plan.accounts.append(acc)
    for key in cancel:
        if key in keys_in_msg:
            continue
        head = reg.correction_target(key, year=year, test=test)
        stored = reg.stored_account(head.doc_ref_id)
        if stored is None:
            raise RegistryError(f"account {key!r}: no stored content to build the deletion from")
        stored.key = key
        stored.doc_ref_id = None
        plan.records.append(RecordPlan(key, ids.doc_ref_id(year), "OECD3", head.doc_ref_id))
        plan.accounts.append(stored)
    targets = [p.corr_doc_ref_id for p in plan.records]
    if len(targets) != len(set(targets)):
        raise RegistryError("the same record would be corrected twice in one message (80011)")
    return plan


def build_correction(
    msg: Message,
    version: Version,
    reg: Registry,
    *,
    test: bool = False,
    cancel: list[str] | None = None,
    out_path: str | Path | None = None,
    now: dt.datetime | None = None,
) -> tuple[BuildResult | None, Plan]:
    """CRS702 with the registry. Returns (None, plan) when nothing changed."""
    plan = plan_correction(msg, reg, test=test, cancel=cancel)
    if not plan.records:
        return None, plan
    corr = msg.model_copy(update={"accounts": plan.accounts, "message_type_indic": "CRS702"})
    _check(corr, version, correction=True)
    result = builder.build(
        corr, version, test=test, now=now, records=plan.records, fi_plan=plan.fi_plan
    )
    return _finish(reg, corr, version, result, test=test, out_path=out_path), plan


def record_outcome(
    reg: Registry, message_ref_id: str, outcome: status.Outcome, *, source: str = ""
) -> str:
    """Apply a parsed portal outcome to the registry; returns the new status."""
    if outcome.accepted is None:
        raise RegistryError("the outcome does not say whether the message was accepted")
    new_status = "accepted" if outcome.accepted else "rejected"
    findings = [
        (f.doc_ref_ids[0] if f.doc_ref_ids else None, f.code, f.details) for f in outcome.findings
    ]
    reg.set_status(message_ref_id, new_status, source=source, findings=findings)
    return new_status
