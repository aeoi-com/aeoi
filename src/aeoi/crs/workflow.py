"""One-call operations for user interfaces (the browser page today): open a registry, decide
what a workbook means against it (new message, correction, both), build and encrypt, record the
portal outcome. Everything is JSON-ready so the page stays a thin renderer; the rules live in
:mod:`aeoi.crs.submit`, :mod:`aeoi.registry` and :mod:`aeoi.estv.packaging`.

The registry is the state. Productive messages and corrections need an open registry (it is
what prevents identifier reuse and makes next year's corrections possible); only test messages
may be built without one.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aeoi.crs import build as builder
from aeoi.crs import check, submit
from aeoi.crs.build import BuildResult
from aeoi.crs.model import Message, Version
from aeoi.estv import ids, packaging, status, titles
from aeoi.messages import Msg, text
from aeoi.registry import Registry, RegistryError, content_hash

PUBLIC_KEY_SETTING = "estv_public_key_pem"


class WorkflowError(ValueError):
    pass


# --- registry ----------------------------------------------------------------------------------


def registry_view(reg: Registry | None) -> dict[str, Any]:
    """What the page shows about the open registry."""
    if reg is None:
        return {"open": False, "messages": [], "counts": {}, "has_key": False}
    messages = []
    counts: dict[str, int] = {}
    for m in reg.messages():
        n = reg.conn.execute(
            "SELECT COUNT(*) FROM records WHERE message_ref_id = ? AND kind = 'AR'",
            (m["message_ref_id"],),
        ).fetchone()[0]
        counts[m["status"]] = counts.get(m["status"], 0) + 1
        messages.append(
            {
                "message_ref_id": m["message_ref_id"],
                "year": m["reporting_year"],
                "version": m["version"],
                "type": m["message_type_indic"],
                "test": bool(m["test"]),
                "created_at": m["created_at"],
                "records": n,
                "status": m["status"],
                "status_updated_at": m["status_updated_at"],
            }
        )
    return {
        "open": True,
        "path": str(reg.path),
        "messages": messages,
        "counts": counts,
        "pending": [m["message_ref_id"] for m in messages if m["status"] in ("built", "submitted")],
        "has_key": bool(reg.get_setting(PUBLIC_KEY_SETTING)),
    }


def remember_public_key(reg: Registry, pem: bytes | str) -> str:
    """Validate and store the ESTV public key in the registry; returns its SHA-256."""
    key = packaging.load_public_key(pem)
    text = pem.decode("utf-8") if isinstance(pem, bytes) else pem
    reg.set_setting(PUBLIC_KEY_SETTING, text)
    from cryptography.hazmat.primitives import serialization

    der = key.public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return packaging.sha256_hex(der)


def public_key_pem(reg: Registry | None, pem: bytes | str | None) -> str | None:
    """The key to use: the one given now, else the remembered one."""
    if pem:
        return pem.decode("utf-8") if isinstance(pem, bytes) else pem
    if reg is not None:
        return reg.get_setting(PUBLIC_KEY_SETTING)
    return None


# --- planning ----------------------------------------------------------------------------------


@dataclass
class Intent:
    """What the workbook means against the registry."""

    year: int
    version: Version
    test: bool
    new_keys: list[str] = field(default_factory=list)  # accounts with no valid record yet
    existing_keys: list[str] = field(default_factory=list)  # accounts with a chain head
    changed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    deletions: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)  # keys whose target is not correctable
    problems: list[str] = field(default_factory=list)
    nil: bool = False

    @property
    def messages(self) -> list[str]:
        out = []
        if self.changed or self.deletions:
            out.append("correction")
        if self.new_keys or (self.nil and not self.existing_keys):
            out.append("new")
        return out

    def as_dict(self, lang: str = "en") -> dict[str, Any]:
        return {
            "year": self.year,
            "version": self.version,
            "test": self.test,
            "new": self.new_keys,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "deletions": self.deletions,
            "blocked": self.blocked,
            "problems": [text(p, lang) for p in self.problems],
            "messages": self.messages,
            "nil": self.nil,
        }


def plan(
    msg: Message,
    version: Version,
    reg: Registry | None,
    *,
    test: bool,
    cancel: list[str] | None = None,
) -> Intent:
    """Classify every account of the workbook against the registry (no side effects)."""
    cancel = list(cancel or [])
    intent = Intent(year=msg.reporting_year, version=version, test=test, nil=not msg.accounts)
    if reg is None:
        intent.new_keys = [a.key for a in msg.accounts]
        if not test:
            intent.problems.append(Msg("wf_no_registry_plan"))
        return intent
    for acc in msg.accounts:
        try:  # correction_target knows every reason a record cannot be corrected (6.x, 80002)
            head = reg.correction_target(acc.key, year=msg.reporting_year, test=test)
        except RegistryError as exc:
            if "nothing sent" in str(exc) or "was deleted" in str(exc):
                intent.new_keys.append(acc.key)  # never sent, or deleted: a new record
            else:
                intent.blocked.append(acc.key)
                intent.problems.append(exc.args[0])
            continue
        intent.existing_keys.append(acc.key)
        if acc.key in cancel:
            intent.deletions.append(acc.key)
        elif content_hash(acc, head.version) == head.content_sha256:
            intent.unchanged.append(acc.key)
        else:
            intent.changed.append(acc.key)
    for key in cancel:
        if key in intent.existing_keys or key in intent.new_keys:
            continue
        try:
            reg.correction_target(key, year=msg.reporting_year, test=test)
            intent.deletions.append(key)
        except RegistryError as exc:
            intent.blocked.append(key)
            intent.problems.append(exc.args[0])
    return intent


# --- building ------------------------------------------------------------------------------------


@dataclass
class Built:
    kind: str  # "new" or "correction"
    result: BuildResult
    package: bytes | None
    package_name: str
    xml_name: str
    info: packaging.PackageInfo | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "message_ref_id": self.result.message_ref_id,
            "records": len(self.result.doc_ref_ids),
            "doc_ref_ids": self.result.doc_ref_ids,
            "package_name": self.package_name,
            "package_bytes": len(self.package) if self.package else 0,
            "xml_name": self.xml_name,
            "xml_bytes": len(self.result.xml.encode("utf-8")),
            "encrypted": self.package is not None,
        }


def _names(msg: Message, message_ref_id: str, *, test: bool) -> tuple[str, str]:
    short = message_ref_id.rsplit("CH", 1)[-1][:8]
    stem = f"{'Test-' if test else ''}CRS-{msg.reporting_year}-{short}"
    return f"{stem}.zip", f"{stem}.xml"


def build(
    msg: Message,
    version: Version,
    reg: Registry | None,
    *,
    test: bool,
    cancel: list[str] | None = None,
    public_key: bytes | str | None = None,
    now: dt.datetime | None = None,
) -> list[Built]:
    """Build every message the workbook implies (correction first, then new records), register
    them, and encrypt each one when a public key is available. Raises WorkflowError with a
    message meant for the user."""
    intent = plan(msg, version, reg, test=test, cancel=cancel)
    if intent.blocked:
        raise WorkflowError(Msg("wf_blocked", problems=intent.problems))
    if reg is None and not test:
        raise WorkflowError(Msg("wf_need_registry"))
    pem = public_key_pem(reg, public_key)
    key = packaging.load_public_key(pem) if pem else None
    outputs: list[Built] = []

    def finish(kind: str, result: BuildResult) -> None:
        package_name, xml_name = _names(msg, result.message_ref_id, test=test)
        package = info = None
        if key is not None:
            package, info = packaging.build_package(
                result.xml.encode("utf-8"), key, file_name=package_name, test=test
            )
        outputs.append(Built(kind, result, package, package_name, xml_name, info))

    if "correction" in intent.messages:
        assert reg is not None
        keep = set(intent.changed) | set(intent.deletions) | set(intent.unchanged)
        corr_msg = msg.model_copy(update={"accounts": [a for a in msg.accounts if a.key in keep]})
        result, _plan = submit.build_correction(
            corr_msg, version, reg, test=test, cancel=intent.deletions, now=now
        )
        if result is not None:
            finish("correction", result)
    if "new" in intent.messages:
        new_msg = msg.model_copy(
            update={"accounts": [a for a in msg.accounts if a.key in intent.new_keys]}
        )
        if not new_msg.accounts:
            new_msg = new_msg.model_copy(update={"message_type_indic": "CRS703"})
        if reg is None:
            result = builder.build(new_msg, version, test=test, now=now)
        else:
            result = submit.build_new(new_msg, version, reg, test=test, now=now)
        finish("new", result)
    if not outputs:
        raise WorkflowError(Msg("wf_nothing_to_send"))
    return outputs


def build_from_workbook(
    path: str | Path,
    version: Version,
    reg: Registry | None,
    *,
    test: bool,
    cancel: list[str] | None = None,
    public_key: bytes | str | None = None,
    now: dt.datetime | None = None,
) -> tuple[check.WorkbookReport, list[Built]]:
    """Check the workbook first; build only when it is clean."""
    report = check.check_workbook(path, version)
    if not report.ok or report.message is None:
        raise WorkflowError(Msg("wf_workbook_errors"))
    return report, build(
        report.message, version, reg, test=test, cancel=cancel, public_key=public_key, now=now
    )


# --- outcomes ------------------------------------------------------------------------------------


def parse_outcome(text_or_xml: str | bytes) -> status.Outcome:
    data = text_or_xml.decode("utf-8", "replace") if isinstance(text_or_xml, bytes) else text_or_xml
    if data.lstrip().startswith("<"):
        return status.parse_status_message(data)
    return status.parse_text(data)


def outcome_view(outcome: status.Outcome, lang: str = "de") -> dict[str, Any]:
    return {
        "accepted": outcome.accepted,
        "message_ref_id": outcome.original_message_ref_id,
        "source": outcome.source,
        "findings": [
            {
                "code": f.code,
                "title": titles.rule_title(f.code, lang),
                "fix": titles.rule_fix(f.code, lang),
                "doc_ref_ids": list(f.doc_ref_ids),
                "details": f.details,
                "official": (f.rule or {}).get("text_de", ""),
                "should_have_been_caught": bool(f.rule and f.rule["status"] == "implemented"),
            }
            for f in outcome.findings
        ],
    }


def record_outcome(
    reg: Registry, text_or_xml: str | bytes, *, message_ref_id: str | None = None, lang: str = "de"
) -> dict[str, Any]:
    """Parse the portal's answer and store it; the MessageRefId comes from the answer or the
    caller (portal text often lacks it)."""
    outcome = parse_outcome(text_or_xml)
    ref = outcome.original_message_ref_id or message_ref_id
    if not ref:
        raise WorkflowError(Msg("wf_no_msgref"))
    if reg.message(ref) is None:
        raise WorkflowError(Msg("wf_not_in_registry", ref=ref))
    if outcome.portal_error:  # not a verdict: the message stays open, the file goes up again
        reg.set_status(ref, "submitted", source=outcome.source)
        view = outcome_view(outcome, lang)
        view.update(message_ref_id=ref, status="submitted", note=Msg("wf_portal_error").text(lang))
        return view
    if outcome.accepted is None:
        raise WorkflowError(Msg("wf_outcome_unknown"))
    new_status = submit.record_outcome(reg, ref, outcome, source=outcome.source)
    view = outcome_view(outcome, lang)
    view.update(message_ref_id=ref, status=new_status)
    return view


def message_ref_id_for(msg: Message, year: int | None = None) -> str:
    """Helper for tests and the page: a fresh MessageRefId in the ESTV format."""
    return ids.message_ref_id(year or msg.reporting_year)
