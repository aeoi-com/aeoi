"""Command line entry point: ``aeoi estv package`` and ``aeoi estv inspect``.

The CRS build/validate/correct commands arrive with the domain model and the rule engine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aeoi import __version__
from aeoi.estv import packaging


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
    test = None if args.test is None else args.test
    result = packaging.inspect_package(
        package, public_key=public_key, file_name=Path(args.package).name, test=test
    )
    print(json.dumps(result.__dict__, indent=2))
    return 0 if result.ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aeoi", description="AEOI reporting toolkit")
    parser.add_argument("--version", action="version", version=f"aeoi {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

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
