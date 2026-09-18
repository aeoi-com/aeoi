"""Rebuild a lost registry from the XML files the institution kept.

Every identifier the ESTV rules need (MessageRefId, DocRefIds, DocTypeIndics, CorrDocRefIds,
ReportingPeriod, test or productive) is inside the files that were uploaded. Two things are not:
the portal's verdict per message - the caller states it, and only files the portal accepted (or
that still wait for a verdict) belong in the registry - and the workbook keys that link a row of
the Excel template to its record. Keys come from the target record for corrections, from the
workbook when one is given (same account number and holder), and from the account number
otherwise.

The packages (.zip) cannot be used: they are encrypted for the ESTV only. Files are the XML
download of the page or the ``--out`` file of ``aeoi crs build``.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aeoi.crs import build as builder
from aeoi.crs import read_xml
from aeoi.crs.model import Account, Message
from aeoi.messages import Msg, text
from aeoi.registry import Registry, RegistryError, identity

RESTORE_STATUSES = ("accepted", "submitted")
_ORDER = {"CRS701": 0, "CRS702": 1}


@dataclass
class RestoredFile:
    name: str
    message_ref_id: str
    year: int
    version: str
    test: bool
    message_type_indic: str
    status: str
    records: int
    keys: dict[str, str] = field(default_factory=dict)  # DocRefId -> account key
    keys_from_workbook: int = 0
    keys_from_number: int = 0
    notes: list[Msg] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return {"CRS702": "correction", "CRS703": "nil"}.get(self.message_type_indic, "new")


@dataclass
class RestoreReport:
    restored: list[RestoredFile] = field(default_factory=list)
    skipped: list[tuple[str, Msg]] = field(default_factory=list)  # file name, reason

    @property
    def accounts(self) -> int:
        return sum(f.records for f in self.restored)

    def as_dict(self, lang: str = "en") -> dict[str, Any]:
        return {
            "restored": [
                {
                    "name": f.name,
                    "message_ref_id": f.message_ref_id,
                    "year": f.year,
                    "version": f.version,
                    "test": f.test,
                    "kind": f.kind,
                    "status": f.status,
                    "records": f.records,
                    "keys": f.keys,
                    "keys_from_workbook": f.keys_from_workbook,
                    "keys_from_number": f.keys_from_number,
                    "notes": [text(n, lang) for n in f.notes],
                }
                for f in self.restored
            ],
            "skipped": [{"name": n, "reason": text(r, lang)} for n, r in self.skipped],
            "accounts": self.accounts,
        }


@dataclass
class _Loaded:
    name: str
    raw: bytes
    parsed: read_xml.ParsedFile
    test: bool
    created_at: str
    wegleitung: bool


def _created_at(timestamp: str) -> str:
    """The MessageSpec Timestamp as the registry stores creation times (UTC ISO, seconds)."""
    try:
        when = dt.datetime.fromisoformat(timestamp)
    except ValueError:
        return dt.datetime.now(tz=dt.UTC).replace(microsecond=0).isoformat()
    if when.tzinfo is None:  # other tools may write local time without an offset
        when = when.replace(tzinfo=dt.UTC)
    return when.astimezone(dt.UTC).replace(microsecond=0).isoformat()


def _productive_indic(indic: str) -> str:
    """OECD11 (test) -> OECD1: the registry stores the productive meaning, the test flag on the
    message."""
    return "OECD" + indic[-1] if len(indic) == 6 and indic.startswith("OECD1") else indic


def _load(name: str, raw: bytes) -> _Loaded:
    try:
        xml = raw.decode("utf-8")
        canonical = builder.canonical_xml(xml)
        parsed = read_xml.parse(canonical.encode("utf-8"))
    except Exception as exc:  # not XML, not CRS, or not close enough to the schema to read
        raise RegistryError(Msg("restore_not_crs", name=name, error=str(exc)[:200])) from exc
    indics = [s.doc_type_indic for s in parsed.account_specs] + [
        parsed.reporting_fi_spec.doc_type_indic
    ]
    test_flags = {len(i) == 6 and i.startswith("OECD1") for i in indics}
    if len(test_flags) != 1:
        raise RegistryError(Msg("restore_mixed_test", name=name))
    return _Loaded(
        name=name,
        raw=raw,
        parsed=parsed,
        test=test_flags.pop(),
        created_at=_created_at(parsed.timestamp),
        wegleitung=builder.is_wegleitung_header(xml),
    )


def _holder_label(acc: Account) -> str:
    if acc.holder_person is not None:
        return f"{acc.holder_person.last_name} {acc.holder_person.first_name}".strip()
    if acc.holder_organisation is not None:
        return acc.holder_organisation.name
    return ""


def _fallback_key(acc: Account, taken: dict[str, str]) -> str:
    """The account number, or number/holder when the number is shared (joint accounts)."""
    key = acc.account_number
    if taken.get(key, identity(acc)) == identity(acc):
        return key
    return f"{acc.account_number}/{_holder_label(acc)}"


def restore(
    reg: Registry,
    files: list[Path] | list[tuple[str, bytes]],
    *,
    status: str = "accepted",
    workbook: Message | None = None,
) -> RestoreReport:
    """Register every file (oldest first, by its Timestamp) with the given portal status.

    Files already in the registry (same MessageRefId) are skipped, as is a file whose DocRefIds
    clash with another message; the report says why. ``workbook`` is the institution's current
    template (``check.check_workbook(...).message``); its keys are adopted for the accounts it
    contains.
    """
    if status not in RESTORE_STATUSES:
        raise RegistryError(Msg("restore_bad_status", status=repr(status)))
    report = RestoreReport()
    loaded: list[_Loaded] = []
    for item in files:
        name, raw = (item.name, item.read_bytes()) if isinstance(item, Path) else item
        try:
            loaded.append(_load(name, raw))
        except RegistryError as exc:
            report.skipped.append((name, exc.args[0]))
    # oldest first; at equal timestamps (one build made both) the new message before the
    # correction, so a correction never precedes a record it could point to
    loaded.sort(
        key=lambda f: (f.created_at, _ORDER.get(f.parsed.message.message_type_indic, 2), f.name)
    )
    by_identity = {identity(a): a.key for a in workbook.accounts} if workbook else {}
    for f in loaded:
        try:
            report.restored.append(_register(reg, f, status, by_identity))
        except RegistryError as exc:
            report.skipped.append((f.name, exc.args[0]))
    return report


def _register(reg: Registry, f: _Loaded, status: str, by_identity: dict[str, str]) -> RestoredFile:
    p = f.parsed
    msg = p.message
    ref = msg.message_ref_id or ""
    if reg.message(ref) is not None:
        raise RegistryError(Msg("restore_already", ref=ref))
    year, test = msg.reporting_year, f.test
    out = RestoredFile(
        name=f.name, message_ref_id=ref, year=year, version=p.version, test=test,
        message_type_indic=msg.message_type_indic, status=status, records=len(msg.accounts),
    )  # fmt: skip
    if f.wegleitung:
        out.notes.append(Msg("restore_wegleitung_header"))
    taken: dict[str, str] = {}  # key -> identity of the account holding it (this year, this mode)
    for head in reg.chain_heads(year=year, test=test):
        acc = reg.stored_account(head.doc_ref_id)
        if acc is not None and head.account_key:
            taken[head.account_key] = identity(acc)
    records: list[tuple[str, Account, str, str | None]] = []
    for acc, spec in zip(msg.accounts, p.account_specs, strict=True):
        if reg.record(spec.doc_ref_id) is not None:
            raise RegistryError(Msg("reg_docref_used", ref=spec.doc_ref_id))
        indic = _productive_indic(spec.doc_type_indic)
        corr = spec.corr_doc_ref_id
        key = None
        if indic in ("OECD2", "OECD3"):  # the chain decides: same key as the corrected record
            target = reg.record(corr) if corr else None
            if target is not None:
                key = target.account_key
            else:
                out.notes.append(
                    Msg("restore_target_missing", ref=corr or "?", doc=spec.doc_ref_id)
                )
        if key is None and identity(acc) in by_identity:
            key = by_identity[identity(acc)]
            out.keys_from_workbook += 1
        if key is None:
            key = _fallback_key(acc, taken)
            out.keys_from_number += 1
        taken.setdefault(key, identity(acc))
        out.keys[spec.doc_ref_id] = key
        records.append((spec.doc_ref_id, acc.model_copy(update={"key": key}), indic, corr))
    fi_spec = p.reporting_fi_spec
    reg.register_message(
        message_ref_id=ref,
        reporting_year=year,
        version=p.version,
        message_type_indic=msg.message_type_indic,
        test=test,
        xml=f.raw.decode("utf-8"),
        xml_path=f.name,
        fi_doc_ref_id=fi_spec.doc_ref_id,
        # an OECD0 whose DocRefId is not known yet is stored too, so later messages resend it
        fi_resend=reg.record(fi_spec.doc_ref_id) is not None,
        fi_doc_type_indic=_productive_indic(fi_spec.doc_type_indic),
        records=records,
        created_at=f.created_at,
        status=status,
        status_source=f"restored from {f.name}",
    )
    if out.keys_from_number and by_identity:
        keys = [k for d, k in out.keys.items() if k not in by_identity.values()]
        out.notes.append(Msg("restore_keys_from_number", n=out.keys_from_number, keys=keys[:5]))
    return out
