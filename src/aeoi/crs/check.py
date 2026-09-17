"""Check a filled workbook (or CSV folder): one function for the CLI and the browser page."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from aeoi.crs import flat, model
from aeoi.crs.model import Message, Version


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

    def lines(self) -> list[str]:
        out = [f"input  | {p}" for p in self.input_problems]
        for p in self.problems:
            level = "info " if p.rule == "info" else "error"
            rule = f" [{p.rule}]" if p.rule else ""
            out.append(f"{level}  | {p.where}: {p.message}{rule}")
        return out

    def headline(self) -> str:
        if self.message is None:
            return "NOT OK: the workbook could not be read"
        return (
            f"{'OK' if self.ok else 'NOT OK'}: {len(self.message.accounts)} account(s), "
            f"reporting year {self.message.reporting_year}, CRS {self.version}, "
            f"{len(self.input_problems)} input problem(s), {len(self.errors)} error(s)"
        )

    def render(self) -> str:
        return "\n".join([self.headline(), *self.lines()])


def check_workbook(
    path: str | Path, version: Version, *, today: dt.date | None = None
) -> WorkbookReport:
    """Read the flat input and run every check for the given schema version."""
    read = flat.read(Path(path))
    report = WorkbookReport(version, read.message, list(read.problems))
    if read.message is not None:
        report.problems = list(model.check_message(read.message, version, today=today).problems)
    return report
