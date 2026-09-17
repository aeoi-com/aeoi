"""Command line entry point.

aeoi crs template  --out template.xlsx [--example]
aeoi crs check     --input filled.xlsx --version 3.0
aeoi crs build     --input filled.xlsx --version 3.0 --out report.xml [--test] [--registry reg.sqlite] [--key ESTV-PublicKey.pem --package Test-report.zip]
aeoi crs correct   --input fixed.xlsx --version 3.0 --out corr.xml --registry reg.sqlite [--cancel KEY ...] [--test] [--key ... --package ...]
aeoi crs registry  --registry reg.sqlite [--discard REF]
aeoi crs validate  report.xml [--test|--prod]
aeoi estv package  --xml report.xml --key ESTV-PublicKey.pem --out Test-report.zip --test
aeoi estv inspect  Test-report.zip [--key ESTV-PublicKey.pem] [--test|--prod]
aeoi estv status   outcome.xml | outcome.txt [--registry reg.sqlite --message CH2026CH...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aeoi import __version__
from aeoi.estv import packaging


def _load_message(path: str, version: str):
    """Read and check the flat input; print every problem; return the message or None."""
    from aeoi.crs.check import check_workbook

    report = check_workbook(path, version)
    for line in report.lines():
        print(line, file=sys.stderr)
    if not report.ok:
        return None, 1
    return report.message, 0


def _cmd_crs_template(args: argparse.Namespace) -> int:
    from aeoi.crs import template

    if args.example:
        from aeoi.crs.example import sample_message

        template.write_message(sample_message(), args.out)
    else:
        template.write_template(args.out)
    print(f"wrote {args.out}")
    return 0


def _cmd_crs_check(args: argparse.Namespace) -> int:
    from aeoi.crs.check import check_workbook

    report = check_workbook(args.input, args.version)
    print(report.render())
    return 0 if report.ok else 1


def _package(result, args, summary: dict) -> int:
    if not args.package:
        return 0
    if not args.key:
        print("error: --package needs --key (ESTV public key PEM)", file=sys.stderr)
        return 2
    public_key = packaging.load_public_key(Path(args.key))
    try:
        info = packaging.write_package(
            result.xml.encode("utf-8"), public_key, args.package, test=args.test
        )
    except packaging.PackagingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    summary["package"] = info.__dict__
    return 0


def _cmd_crs_build(args: argparse.Namespace) -> int:
    from aeoi.crs import build, xsd

    msg, rc = _load_message(args.input, args.version)
    if msg is None:
        return rc
    if args.registry:
        from aeoi.crs import submit
        from aeoi.registry import Registry, RegistryError

        try:
            with Registry(args.registry) as reg:
                result = submit.build_new(msg, args.version, reg, test=args.test, out_path=args.out)
        except RegistryError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    else:
        result = build.build(msg, args.version, test=args.test)
        xsd_errors = xsd.validate(result.xml, args.version)
        if xsd_errors:  # never hand over a file the portal would reject with 50007
            for e in xsd_errors:
                print(f"xsd    | {e}", file=sys.stderr)
            print(
                "error: built XML is not valid against the OECD schema; nothing written",
                file=sys.stderr,
            )
            return 1
        Path(args.out).write_text(result.xml, encoding="utf-8")
    summary = {
        "xml": args.out,
        "version": result.version,
        "message_ref_id": result.message_ref_id,
        "reporting_fi_doc_ref_id": result.reporting_fi_doc_ref_id,
        "doc_ref_ids": result.doc_ref_ids,
        "test": args.test,
        "registry": args.registry,
    }
    rc = _package(result, args, summary)
    if rc:
        return rc
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_crs_correct(args: argparse.Namespace) -> int:
    from aeoi.crs import flat, submit
    from aeoi.registry import Registry, RegistryError

    read = flat.read(Path(args.input))
    for p in read.problems:
        print(f"input  | {p}", file=sys.stderr)
    if read.message is None or read.problems:
        return 1
    try:
        with Registry(args.registry) as reg:
            result, plan = submit.build_correction(
                read.message,
                args.version,
                reg,
                test=args.test,
                cancel=args.cancel or [],
                out_path=args.out,
            )
    except RegistryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if result is None:
        print(f"nothing to correct: {len(plan.skipped_unchanged)} account(s) unchanged")
        return 0
    summary = {
        "xml": args.out,
        "version": result.version,
        "message_ref_id": result.message_ref_id,
        "message_type_indic": "CRS702",
        "records": [
            {
                "key": p.key,
                "doc_type_indic": p.doc_type_indic,
                "doc_ref_id": p.doc_ref_id,
                "corr_doc_ref_id": p.corr_doc_ref_id,
            }
            for p in result.records
        ],
        "skipped_unchanged": plan.skipped_unchanged,
        "test": args.test,
    }
    rc = _package(result, args, summary)
    if rc:
        return rc
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_crs_validate(args: argparse.Namespace) -> int:
    from aeoi.crs import validate

    test = None if args.test is None else args.test
    rep = validate.validate_file(args.file, test=test)
    print(rep.render())
    return 0 if rep.ok else 1


def _cmd_crs_registry(args: argparse.Namespace) -> int:
    from aeoi.crs import submit
    from aeoi.registry import Registry, RegistryError

    with Registry(args.registry) as reg:
        if args.discard:
            try:
                submit.discard(reg, args.discard)
            except RegistryError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
            print(f"discarded {args.discard}")
        print(reg.summary())
    return 0


def _cmd_estv_package(args: argparse.Namespace) -> int:
    xml = Path(args.xml).read_bytes()
    public_key = packaging.load_public_key(Path(args.key))
    try:
        info = packaging.write_package(xml, public_key, args.out, test=args.test)
    except packaging.PackagingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(info.__dict__, indent=2))
    return 0


def _cmd_estv_inspect(args: argparse.Namespace) -> int:
    package = Path(args.package).read_bytes()
    public_key = packaging.load_public_key(Path(args.key)) if args.key else None
    result = packaging.inspect_package(
        package, public_key=public_key, file_name=Path(args.package).name, test=args.test
    )
    print(json.dumps(result.__dict__, indent=2))
    return 0 if result.ok else 1


def _cmd_estv_status(args: argparse.Namespace) -> int:
    from aeoi.estv import status

    path = Path(args.file)
    raw = path.read_bytes()
    if raw.lstrip().startswith(b"<"):
        outcome = status.parse_status_message(raw)
    else:
        outcome = status.parse_text(raw.decode("utf-8", "replace"))
    print(status.render(outcome))
    if args.registry:
        from aeoi.crs import submit
        from aeoi.registry import Registry, RegistryError

        ref = args.message or outcome.original_message_ref_id
        if not ref:
            print("error: --message needed, the outcome does not name the message", file=sys.stderr)
            return 2
        try:
            with Registry(args.registry) as reg:
                new = submit.record_outcome(reg, ref, outcome, source=str(path))
        except RegistryError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"registry: {ref} -> {new}")
    return 0 if outcome.accepted else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aeoi", description="AEOI reporting toolkit")
    parser.add_argument("--version", action="version", version=f"aeoi {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    crs = sub.add_parser("crs", help="CRS reporting (OECD schema 2.0 / 3.0)")
    crs_sub = crs.add_subparsers(dest="crs_command", required=True)

    t = crs_sub.add_parser("template", help="write the Excel input template")
    t.add_argument("--out", required=True, help="path of the .xlsx to write")
    t.add_argument("--example", action="store_true", help="fill it with invented example data")
    t.set_defaults(func=_cmd_crs_template)

    c = crs_sub.add_parser("check", help="read the input and report every problem")
    c.add_argument("--input", required=True, help=".xlsx workbook or folder of <Sheet>.csv files")
    c.add_argument("--version", default="3.0", choices=["2.0", "3.0"], help="CRS schema version")
    c.set_defaults(func=_cmd_crs_check)

    b = crs_sub.add_parser("build", help="read, check and write the CRS XML (optionally packaged)")
    b.add_argument("--input", required=True)
    b.add_argument("--version", default="3.0", choices=["2.0", "3.0"])
    b.add_argument("--out", required=True, help="XML file to write")
    b.add_argument("--test", action="store_true", help="test message (OECD11 DocTypeIndic)")
    b.add_argument("--key", help="ESTV public key PEM, needed with --package")
    b.add_argument("--package", help="also write the encrypted ESTV package (zip) to this path")
    b.add_argument("--registry", help="submission registry (SQLite): identifiers and status")
    b.set_defaults(func=_cmd_crs_build)

    co = crs_sub.add_parser("correct", help="build a CRS702 correction/deletion message")
    co.add_argument("--input", required=True, help="workbook with the corrected rows")
    co.add_argument("--version", default="3.0", choices=["2.0", "3.0"])
    co.add_argument("--out", required=True)
    co.add_argument("--registry", required=True)
    co.add_argument("--cancel", action="append", metavar="KEY", help="delete this account (OECD3)")
    co.add_argument("--test", action="store_true")
    co.add_argument("--key")
    co.add_argument("--package")
    co.set_defaults(func=_cmd_crs_correct)

    va = crs_sub.add_parser("validate", help="check an existing CRS XML file like the portal would")
    va.add_argument("file")
    g2 = va.add_mutually_exclusive_group()
    g2.add_argument("--test", dest="test", action="store_true", default=None,
                    help="treat as a test file (default: from the file name)")  # fmt: skip
    g2.add_argument("--prod", dest="test", action="store_false")
    va.set_defaults(func=_cmd_crs_validate)

    rg = crs_sub.add_parser("registry", help="list the messages of a registry")
    rg.add_argument("--registry", required=True)
    rg.add_argument(
        "--discard",
        metavar="MESSAGE_REF_ID",
        help="mark a built, never uploaded message as discarded",
    )
    rg.set_defaults(func=_cmd_crs_registry)

    estv = sub.add_parser("estv", help="Swiss ESTV AIA portal tools")
    estv_sub = estv.add_subparsers(dest="estv_command", required=True)

    p = estv_sub.add_parser("package", help="zip + AES-256-CBC + RSA package for the ESTV upload")
    p.add_argument("--xml", required=True, help="CRS XML file (will be stored as CRS_Payload.xml)")
    p.add_argument("--key", required=True, help="ESTV public key or certificate (PEM)")
    p.add_argument(
        "--out", required=True, help="output zip; must start with 'Test' for test messages"
    )
    p.add_argument("--test", action="store_true", help="build a test package (Test*.zip)")
    p.set_defaults(func=_cmd_estv_package)

    i = estv_sub.add_parser("inspect", help="structural check of a transfer package")
    i.add_argument("package")
    i.add_argument("--key", help="ESTV public key (PEM) to check the CRS_KEY size")
    g = i.add_mutually_exclusive_group()
    g.add_argument("--test", dest="test", action="store_true", default=None)
    g.add_argument("--prod", dest="test", action="store_false")
    i.set_defaults(func=_cmd_estv_inspect)

    st = estv_sub.add_parser(
        "status", help="read a validation outcome (OECD status message XML or portal text)"
    )
    st.add_argument("file", help="status message .xml, or a text file pasted from the portal")
    st.add_argument("--registry", help="record the outcome in this registry")
    st.add_argument("--message", help="MessageRefId the outcome belongs to (if the file lacks it)")
    st.set_defaults(func=_cmd_estv_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
