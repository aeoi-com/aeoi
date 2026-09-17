"""Structured view of a check result for user interfaces: the browser page renders the JSON,
the CLI may later use the same titles. Nothing here changes what is checked.
"""

from __future__ import annotations

import re
from collections import Counter
from decimal import Decimal
from typing import Any

from aeoi.crs import check, model, validate
from aeoi.estv import status, titles
from aeoi.messages import text

_XPATH_ACCOUNT = re.compile(r"AccountReport\[(\d+)\]")
_KEY_ACCOUNT = re.compile(r"Accounts\[key=([^\]]+)\]")
_CP = re.compile(r"controlling_persons\[(\d+)\]|ControllingPerson\[(\d+)\]")


def locate(where: str) -> dict[str, Any]:
    """Map a ``where`` string (model path or XPath) to a scope the page can label."""
    loc: dict[str, Any] = {"scope": "file", "field": where.rsplit("/", 1)[-1].rsplit(".", 1)[-1]}
    loc["field"] = re.sub(r"^\w+:", "", loc["field"])
    account = _KEY_ACCOUNT.search(where) or _XPATH_ACCOUNT.search(where)
    header = (
        "MessageSpec" in where
        or where.startswith("CRS_OECD")
        or where in ("xsd", "CrsBody")
        or (where.startswith("/") and "ReportingGroup" not in where)
    )
    if account:
        loc.update(scope="account", ref=account.group(1))
    elif "ReportingFI" in where:
        loc["scope"] = "fi"
    elif header:
        loc["scope"] = "header"
    if m := _CP.search(where):
        loc["controlling_person"] = int(m.group(1) or m.group(2))
    return loc


def problem_dict(p: model.Problem, lang: str, severity: str = "error") -> dict[str, Any]:
    rule = p.rule or "aeoi"
    entry = status.catalogue().get(rule)
    return {
        "severity": severity,
        "rule": p.rule,
        "where": p.where,
        "message": text(p.message, lang),
        "title": titles.rule_title(rule, lang),
        "fix": titles.rule_fix(rule, lang),
        "official": (entry or {}).get("text_de", ""),
        "origin": (entry or {}).get("origin", "estv" if p.rule[:1].isdigit() else "aeoi"),
        **locate(p.where),
    }


def message_overview(msg: model.Message) -> dict[str, Any]:
    residence: Counter[str] = Counter()
    currencies: Counter[str] = Counter()
    holder_types: Counter[str] = Counter()
    account_types: Counter[str] = Counter()
    balances: dict[str, Decimal] = {}
    individuals = organisations = controlling = closed = undocumented = dormant = joint = 0
    for a in msg.accounts:
        if a.holder_person is not None:
            individuals += 1
            holder_types["individual"] += 1
            countries = a.holder_person.residence_countries
        else:
            organisations += 1
            holder_types[
                a.holder_organisation.acct_holder_type if a.holder_organisation else "?"
            ] += 1
            countries = a.holder_organisation.residence_countries if a.holder_organisation else []
        for c in dict.fromkeys(countries):
            residence[c] += 1
        controlling += len(a.controlling_persons)
        closed += a.closed
        undocumented += a.undocumented
        dormant += a.dormant
        joint += a.joint_account_number is not None
        currencies[a.currency] += 1
        balances[a.currency] = balances.get(a.currency, Decimal(0)) + a.balance
        if a.account_type:
            account_types[a.account_type] += 1
    return {
        "fi_name": msg.reporting_fi.name,
        "estv_id": msg.reporting_fi.estv_id,
        "year": msg.reporting_year,
        "message_type_indic": msg.message_type_indic,
        "nil": not msg.accounts,
        "accounts": len(msg.accounts),
        "individuals": individuals,
        "organisations": organisations,
        "controlling_persons": controlling,
        "closed": closed,
        "undocumented": undocumented,
        "dormant": dormant,
        "joint": joint,
        "residence": [{"code": c, "count": n} for c, n in residence.most_common()],
        "currencies": dict(currencies.most_common()),
        "balances": {c: str(v) for c, v in balances.items()},
        "holder_types": dict(holder_types.most_common()),
        "account_types": dict(account_types.most_common()),
    }


def report_dict(
    report: validate.ValidationReport | check.WorkbookReport, lang: str = "de"
) -> dict[str, Any]:
    """JSON-ready view of either report kind (same shape for the page)."""
    if isinstance(report, validate.ValidationReport):
        problems = [problem_dict(p, lang) for p in report.problems]
        problems += [problem_dict(p, lang, "info") for p in report.infos]
        message = report.message
        kind = "xml"
        version = report.version
    else:
        problems = [
            {
                "severity": "input",
                "rule": "input",
                "where": p.location,
                "message": text(p.message, lang),
                "title": titles.rule_title("input", lang),
                "fix": titles.rule_fix("input", lang),
                "official": "",
                "origin": "aeoi",
                "scope": "workbook",
                "field": p.column or "",
                "sheet": p.sheet,
                "row": p.row,
            }
            for p in report.input_problems
        ]
        problems += [
            problem_dict(p, lang, "info" if p.rule == "info" else "error") for p in report.problems
        ]
        message = report.message
        kind = "workbook"
        version = report.version
    counts = Counter(p["severity"] for p in problems)
    return {
        "kind": kind,
        "ok": report.ok,
        "version": version,
        "headline": report.render(lang).split("\n", 1)[0],
        "text": report.render(lang),
        "counts": {"error": counts["error"], "input": counts["input"], "info": counts["info"]},
        "problems": problems,
        "overview": message_overview(message) if message is not None else None,
    }
