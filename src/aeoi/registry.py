"""Local submission registry: what was sent, under which identifiers, with which outcome.

One SQLite file per reporting FI, on the reporting FI's machine (it contains the account data
needed to build cancellations, so it is personal data: keep it with the workbook, back it up,
never send it). It is the memory the ESTV rules assume the FI has (Wegleitung Ziffer 6):

- ``messages``: every built message (MessageRefId, year, version, type, test flag, hash of the
  XML, status: built / submitted / accepted / rejected).
- ``records``: every DocSpec written (ReportingFI and AccountReports) with its DocTypeIndic,
  the CorrDocRefId it points to, the account key, a hash of the account content, the account
  content itself (JSON) and the ResCountryCodes, plus ``superseded_by`` for correction chains.
- ``findings``: codes returned by the portal, per message and DocRefId.

Rules enforced here (the "registry" family of docs/ESTV-RULES.md): 50009 MessageRefId never
reused; 80000 DocRefId never reused; 80002 CorrDocRefId is a DocRefId sent earlier by this FI;
80003 / 98103 only the last valid link of a chain can be corrected, and a deleted record cannot;
80005 corrections and deletions carry a CorrDocRefId; 80008 / 98102 the ReportingFI is resent
with its DocRefId, AccountReports never; 80010 / 80011 by construction of the correction
message; 98009 no nil report while valid records exist for the year; 98204 a deletion carries
the ResCountryCodes of the deleted record (the stored content is reused).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from aeoi.crs.model import Account

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    message_ref_id TEXT PRIMARY KEY,
    reporting_year INTEGER NOT NULL,
    version TEXT NOT NULL,
    message_type_indic TEXT NOT NULL,
    test INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    xml_sha256 TEXT NOT NULL,
    xml_path TEXT,
    status TEXT NOT NULL DEFAULT 'built',
    status_updated_at TEXT,
    status_source TEXT
);
CREATE TABLE IF NOT EXISTS records (
    doc_ref_id TEXT PRIMARY KEY,
    message_ref_id TEXT NOT NULL REFERENCES messages(message_ref_id),
    kind TEXT NOT NULL,                 -- 'FI' or 'AR'
    account_key TEXT,
    doc_type_indic TEXT NOT NULL,       -- OECD0/1/2/3 (productive meaning; test flag on message)
    corr_doc_ref_id TEXT,
    content_sha256 TEXT,
    content_json TEXT,
    res_country_codes TEXT,
    superseded_by TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS records_key ON records(account_key);
CREATE INDEX IF NOT EXISTS records_msg ON records(message_ref_id);
CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_ref_id TEXT NOT NULL,
    doc_ref_id TEXT,
    code TEXT NOT NULL,
    details TEXT,
    recorded_at TEXT NOT NULL
);
"""

VALID_STATUSES = ("built", "submitted", "accepted", "rejected")


class RegistryError(ValueError):
    """A rule of Wegleitung Ziffer 6 / 5.3.x would be violated (the ESTV code is in the text)."""


def content_hash(acc: Account) -> str:
    """Hash of the account's reportable content (key and DocRefId excluded)."""
    data = acc.model_dump(mode="json", exclude={"key", "doc_ref_id"})
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def res_country_codes(acc: Account) -> list[str]:
    codes: set[str] = set()
    if acc.holder_person is not None:
        codes.update(acc.holder_person.residence_countries)
    if acc.holder_organisation is not None:
        codes.update(acc.holder_organisation.residence_countries)
    for cp in acc.controlling_persons:
        codes.update(cp.person.residence_countries)
    return sorted(codes)


def _now() -> str:
    return dt.datetime.now(tz=dt.UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class RecordRow:
    doc_ref_id: str
    message_ref_id: str
    kind: str
    account_key: str | None
    doc_type_indic: str
    corr_doc_ref_id: str | None
    content_sha256: str | None
    res_country_codes: list[str]
    superseded_by: str | None
    message_status: str
    test: bool
    reporting_year: int

    @property
    def valid(self) -> bool:
        """A valid link: not rejected, not superseded, not a deletion."""
        return (
            self.message_status != "rejected"
            and self.superseded_by is None
            and self.doc_type_indic != "OECD3"
        )


class Registry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> Registry:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # --- queries ---------------------------------------------------------------------------

    def message(self, message_ref_id: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM messages WHERE message_ref_id = ?", (message_ref_id,)
        ).fetchone()

    def messages(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM messages ORDER BY created_at").fetchall()

    def record(self, doc_ref_id: str) -> RecordRow | None:
        row = self.conn.execute(
            "SELECT r.*, m.status AS message_status, m.test AS test, m.reporting_year AS year "
            "FROM records r JOIN messages m ON m.message_ref_id = r.message_ref_id "
            "WHERE r.doc_ref_id = ?",
            (doc_ref_id,),
        ).fetchone()
        return self._row(row) if row else None

    def _row(self, row: sqlite3.Row) -> RecordRow:
        return RecordRow(
            doc_ref_id=row["doc_ref_id"],
            message_ref_id=row["message_ref_id"],
            kind=row["kind"],
            account_key=row["account_key"],
            doc_type_indic=row["doc_type_indic"],
            corr_doc_ref_id=row["corr_doc_ref_id"],
            content_sha256=row["content_sha256"],
            res_country_codes=json.loads(row["res_country_codes"] or "[]"),
            superseded_by=row["superseded_by"],
            message_status=row["message_status"],
            test=bool(row["test"]),
            reporting_year=int(row["year"]),
        )

    def chain_head(self, account_key: str, *, year: int, test: bool) -> RecordRow | None:
        """The last valid AccountReport link for this account key in this year (test/prod)."""
        rows = self.conn.execute(
            "SELECT r.*, m.status AS message_status, m.test AS test, m.reporting_year AS year "
            "FROM records r JOIN messages m ON m.message_ref_id = r.message_ref_id "
            "WHERE r.kind = 'AR' AND r.account_key = ? AND m.reporting_year = ? AND m.test = ? "
            "ORDER BY r.created_at DESC, r.rowid DESC",
            (account_key, year, int(test)),
        ).fetchall()
        for row in rows:
            rec = self._row(row)
            if rec.valid:
                return rec
        return None

    def chain_heads(self, *, year: int, test: bool) -> list[RecordRow]:
        rows = self.conn.execute(
            "SELECT r.*, m.status AS message_status, m.test AS test, m.reporting_year AS year "
            "FROM records r JOIN messages m ON m.message_ref_id = r.message_ref_id "
            "WHERE r.kind = 'AR' AND m.reporting_year = ? AND m.test = ? ORDER BY r.created_at, r.rowid",
            (year, int(test)),
        ).fetchall()
        heads: dict[str, RecordRow] = {}
        for row in rows:
            rec = self._row(row)
            if rec.valid:
                heads[rec.account_key or rec.doc_ref_id] = rec
            elif rec.doc_type_indic == "OECD3" and rec.message_status != "rejected":
                heads.pop(rec.account_key or "", None)
        return list(heads.values())

    def stored_account(self, doc_ref_id: str) -> Account | None:
        row = self.conn.execute(
            "SELECT content_json FROM records WHERE doc_ref_id = ?", (doc_ref_id,)
        ).fetchone()
        if not row or not row["content_json"]:
            return None
        return Account.model_validate_json(row["content_json"])

    def fi_doc_ref_id(self, *, year: int, test: bool) -> str | None:
        """DocRefId of the ReportingFI to resend (OECD0), if one was sent and not rejected."""
        row = self.conn.execute(
            "SELECT r.doc_ref_id FROM records r JOIN messages m ON m.message_ref_id = r.message_ref_id "
            "WHERE r.kind = 'FI' AND m.reporting_year = ? AND m.test = ? AND m.status != 'rejected' "
            "ORDER BY r.created_at DESC, r.rowid DESC LIMIT 1",
            (year, int(test)),
        ).fetchone()
        return row["doc_ref_id"] if row else None

    def has_valid_records(self, *, year: int, test: bool) -> bool:
        return bool(self.chain_heads(year=year, test=test))

    # --- guards (before building) -------------------------------------------------------------

    def assert_message_ref_id_unused(self, message_ref_id: str) -> None:
        if self.message(message_ref_id):
            raise RegistryError(f"MessageRefId {message_ref_id} was already used (50009)")

    def assert_doc_ref_id_unused(self, doc_ref_id: str) -> None:
        if self.record(doc_ref_id):
            raise RegistryError(f"DocRefId {doc_ref_id} was already used (80000)")

    def correction_target(self, account_key: str, *, year: int, test: bool) -> RecordRow:
        """The DocRefId a correction or deletion of this account must reference."""
        head = self.chain_head(account_key, year=year, test=test)
        if head is None:
            rows = self.conn.execute(
                "SELECT r.*, m.status AS message_status, m.test AS test, m.reporting_year AS year "
                "FROM records r JOIN messages m ON m.message_ref_id = r.message_ref_id "
                "WHERE r.kind = 'AR' AND r.account_key = ? AND m.reporting_year = ? AND m.test = ? "
                "ORDER BY r.created_at DESC, r.rowid DESC LIMIT 1",
                (account_key, year, int(test)),
            ).fetchall()
            if not rows:
                raise RegistryError(
                    f"account {account_key!r}: nothing sent for {year} - new accounts go into a "
                    "new message (CRS701), not a correction (80002)"
                )
            last = self._row(rows[0])
            if last.doc_type_indic == "OECD3":
                raise RegistryError(
                    f"account {account_key!r} was deleted ({last.doc_ref_id}); a deleted record "
                    "cannot be corrected - send it again as a new record (98103, 6.4.7)"
                )
            if last.message_status == "rejected":
                raise RegistryError(
                    f"account {account_key!r}: the last message was rejected; fix and send it as "
                    "a new record (80002)"
                )
            raise RegistryError(f"account {account_key!r}: no valid record to correct (80002)")
        if head.message_status == "built":
            raise RegistryError(
                f"account {account_key!r}: message {head.message_ref_id} has no recorded outcome "
                "yet; record the portal result before correcting (80002)"
            )
        return head

    # --- writes ----------------------------------------------------------------------------------

    def register_message(
        self,
        *,
        message_ref_id: str,
        reporting_year: int,
        version: str,
        message_type_indic: str,
        test: bool,
        xml: str,
        xml_path: str | None,
        fi_doc_ref_id: str,
        fi_resend: bool,
        records: list[tuple[str, Account, str, str | None]],
    ) -> None:
        """Store a built message: (doc_ref_id, account, doc_type_indic, corr_doc_ref_id) per record."""
        self.assert_message_ref_id_unused(message_ref_id)
        for doc_ref_id, _, _, _ in records:
            self.assert_doc_ref_id_unused(doc_ref_id)
        if not fi_resend:
            self.assert_doc_ref_id_unused(fi_doc_ref_id)
        now = _now()
        with self.conn:
            self.conn.execute(
                "INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    message_ref_id, reporting_year, version, message_type_indic, int(test), now,
                    hashlib.sha256(xml.encode("utf-8")).hexdigest(), xml_path, "built", None, None,
                ),
            )  # fmt: skip
            if not fi_resend:
                self.conn.execute(
                    "INSERT INTO records (doc_ref_id, message_ref_id, kind, doc_type_indic, created_at)"
                    " VALUES (?,?,?,?,?)",
                    (fi_doc_ref_id, message_ref_id, "FI", "OECD1", now),
                )
            for doc_ref_id, acc, indic, corr in records:
                self.conn.execute(
                    "INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        doc_ref_id, message_ref_id, "AR", acc.key, indic, corr, content_hash(acc),
                        acc.model_dump_json(exclude={"doc_ref_id"}),
                        json.dumps(res_country_codes(acc)), None, now,
                    ),
                )  # fmt: skip
                if corr:
                    self.conn.execute(
                        "UPDATE records SET superseded_by = ? WHERE doc_ref_id = ?",
                        (doc_ref_id, corr),
                    )

    def set_status(
        self,
        message_ref_id: str,
        status: str,
        *,
        source: str = "",
        findings: list[tuple[str | None, str, str]] | None = None,
    ) -> None:
        """Record the portal outcome. A rejected correction message frees its targets again."""
        if status not in VALID_STATUSES:
            raise RegistryError(f"unknown status {status!r}")
        msg = self.message(message_ref_id)
        if msg is None:
            raise RegistryError(f"unknown MessageRefId {message_ref_id}")
        now = _now()
        with self.conn:
            self.conn.execute(
                "UPDATE messages SET status = ?, status_updated_at = ?, status_source = ? "
                "WHERE message_ref_id = ?",
                (status, now, source, message_ref_id),
            )
            if status == "rejected":
                for row in self.conn.execute(
                    "SELECT doc_ref_id, corr_doc_ref_id FROM records WHERE message_ref_id = ?",
                    (message_ref_id,),
                ).fetchall():
                    if row["corr_doc_ref_id"]:
                        self.conn.execute(
                            "UPDATE records SET superseded_by = NULL WHERE doc_ref_id = ? "
                            "AND superseded_by = ?",
                            (row["corr_doc_ref_id"], row["doc_ref_id"]),
                        )
            for doc_ref_id, code, details in findings or []:
                self.conn.execute(
                    "INSERT INTO findings (message_ref_id, doc_ref_id, code, details, recorded_at) "
                    "VALUES (?,?,?,?,?)",
                    (message_ref_id, doc_ref_id, code, details, now),
                )

    def summary(self) -> str:
        lines = []
        for m in self.messages():
            n = self.conn.execute(
                "SELECT COUNT(*) FROM records WHERE message_ref_id = ? AND kind = 'AR'",
                (m["message_ref_id"],),
            ).fetchone()[0]
            flag = " TEST" if m["test"] else ""
            lines.append(
                f"{m['created_at']}  {m['message_ref_id']}  {m['reporting_year']} CRS {m['version']} "
                f"{m['message_type_indic']}{flag}  {n} record(s)  {m['status']}"
            )
        return "\n".join(lines) if lines else "(empty registry)"
