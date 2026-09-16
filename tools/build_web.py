"""Assemble the static browser validator in web/: copy the built wheel next to index.html and
pin its file name in the page. Run after ``python -m build``.

    python tools/build_web.py

Publish the web/ folder as-is (GitHub Pages, any static host). The page has no server side.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def main() -> int:
    wheels = sorted((ROOT / "dist").glob("aeoi-*-py3-none-any.whl"))
    if not wheels:
        print("no wheel in dist/: run python -m build first")
        return 1
    wheel = wheels[-1]
    for old in WEB.glob("aeoi-*.whl"):
        old.unlink()
    shutil.copy(wheel, WEB / wheel.name)
    page = WEB / "index.html"
    text = page.read_text(encoding="utf-8")
    text, n = re.subn(r'const WHEEL = "aeoi-[^"]+\.whl";', f'const WHEEL = "{wheel.name}";', text)
    if n != 1:
        print("WHEEL constant not found in web/index.html")
        return 1
    page.write_text(text, encoding="utf-8")
    print(f"web/ ready: index.html + {wheel.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
