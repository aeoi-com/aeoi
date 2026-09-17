"""Check a filled workbook (or CSV folder): one function for the CLI and the browser page."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from aeoi.crs import flat, model
from aeoi.crs.model import Message, Version
from aeoi.messages import Msg, text


@dataclass
class WorkbookReport:
    version: Version
    message: Message | None
    input_problems: list[flat.InputProblem] = field(default_factory=list)
    problems: list[model.Problem] = field(default_factory=list)

    @property
    def errors(self) -> list[model.Problem]:
        return [p for p in self.problems if p.rule != "info"]

    @property
    def ok(self) -> bool:
        return self.message is not None and not self.input_problems and not self.errors

    def lines(self, lang: str = "en") -> list[str]:
        label = {k: Msg(f"label_{k}").text(lang) for k in ("input", "info", "error")}
        out = [
            f"{label['input']:<6} | {p.location}: {text(p.message, lang)}"
            for p in self.input_problems
        ]
        for p in self.problems:
            level = label["info"] if p.rule == "info" else label["error"]
            rule = f" [{p.rule}]" if p.rule else ""
            out.append(f"{level:<6} | {p.where}: {text(p.message, lang)}{rule}")
        return out

    def headline(self, lang: str = "en") -> str:
        if self.message is None:
            return Msg("report_head_unreadable").text(lang)
        return Msg(
            "report_head_workbook",
            verdict=Msg("verdict_ok" if self.ok else "verdict_not_ok"),
            accounts=Msg("n_accounts", n=len(self.message.accounts)),
            year=self.message.reporting_year,
            version=self.version,
            inputs=Msg("n_inputs", n=len(self.input_problems)),
            errors=Msg("n_errors", n=len(self.errors)),
        ).text(lang)

    def render(self, lang: str = "en") -> str:
        return "\n".join([self.headline(lang), *self.lines(lang)])


def check_workbook(
    path: str | Path, version: Version, *, today: dt.date | None = None
) -> WorkbookReport:
    """Read the flat input and run every check for the given schema version."""
    read = flat.read(Path(path))
    report = WorkbookReport(version, read.message, list(read.problems))
    if read.message is not None:
        report.problems = list(model.check_message(read.message, version, today=today).problems)
    return report
