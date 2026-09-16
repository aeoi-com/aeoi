"""Command line entry point.

aeoi crs template  --out template.xlsx [--example]
aeoi crs check     --input filled.xlsx --version 3.0
aeoi crs build     --input filled.xlsx --version 3.0 --out report.xml [--test] [--key ESTV-PublicKey.pem --package Test-report.zip]
aeoi estv package  --xml report.xml --key ESTV-PublicKey.pem --out Test-report.zip --test
aeoi estv inspect  Test-report.zip [--key ESTV-PublicKey.pem] [--test|--prod]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aeoi import __version__
from aeoi.estv import packaging


def _load_message(path: str, version: str):
    """Read the flat input and check it; print problems; return the message or None."""
    from aeoi.crs import flat, model

    result = flat.read(Path(path))
    for p in result.problems:
        print(f"input  | {p}", file=sys.stderr)
    if result.message is None:
        return None, 1
    report = model.check_message(result.message, version)
    errors = 0
    for p in report.problems:
        level = "info " if p.rule == "info" else "error"
        rule = f" [{p.rule}]" if p.rule else ""
        print(f"{level}  | {p.where}: {p.message}{rule}", file=sys.stderr)
        errors += p.rule != "info"
    if result.problems or errors:
        return None, 1
    return result.message, 0


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
    msg, rc = _load_message(args.input, args.version)
    if msg is not None:
        print(
            f"ok: {len(msg.accounts)} account(s), reporting year {msg.reporting_year}, CRS {args.version}"
        )
    return rc


def _cmd_crs_build(args: argparse.Namespace) -> int:
    from aeoi.crs import build, xsd

    msg, rc = _load_message(args.input, args.version)
    if msg is None:
        return rc
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
    }
    if args.package:
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
    print(json.dumps(summary, indent=2))
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
    b.set_defaults(func=_cmd_crs_build)

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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
