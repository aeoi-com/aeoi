"""Assemble the static browser app in web/ so that it is served from one origin only:

- the built aeoi wheel (from dist/),
- the Pyodide runtime and the packages the page needs (dependency closure computed from the
  official pyodide-lock.json; a pruned lock file is written next to them),
- the pure-Python wheels from PyPI (xmlschema, xsdata, openpyxl and their dependencies),
- the service worker with the precache list (offline after the first visit).

    python -m build && python tools/build_web.py

Downloads are cached in .local/vendor-cache (or $AEOI_VENDOR_CACHE) and verified by size; the
result is web/pyodide/, web/wheels/, web/sw.js and web/vendor.json - all ignored by git. Publish
the web/ folder as-is; the page has no server side and contacts no other host.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
CACHE = Path(os.environ.get("AEOI_VENDOR_CACHE", ROOT / ".local" / "vendor-cache"))

PYODIDE_VERSION = "0.27.7"
PYODIDE_BASE = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"
PYODIDE_CORE = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip"]
PYODIDE_PACKAGES = ["lxml", "pydantic", "micropip", "cryptography", "sqlite3"]
# pure-Python wheels installed with deps=False, so every dependency is listed explicitly;
# xsdata 26 needs typing-extensions >= 4.12 while the Pyodide pydantic ships 4.11
PYPI_WHEELS = ["xmlschema", "elementpath", "xsdata==24.12", "openpyxl", "et_xmlfile"]
STATIC = ["index.html", "app.html", "preise.html", "ueber-uns.html", "kontakt.html", "impressum.html", "datenschutz.html", "agb.html", "fehlercodes.html",
          "app.js", "flow.js", "i18n.js", "i18n-flow.js", "site.js", "site-i18n.js", "site-i18n-agb.js", "site-i18n-pages.js", "styles.css", "site.css", "manifest.webmanifest",
          "icon.svg", "icon-maskable.svg", "logo.svg", "logo-mark.svg", "fonts/inter-latin.woff2", "fonts/inter-latin-ext.woff2"]  # fmt: skip


def log(msg: str) -> None:
    print(msg, flush=True)


def fetch(url: str, dest: Path, expected_size: int | None = None) -> Path:
    """Download once into the cache; a wrong size means a broken download and is retried once."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in (1, 2):
        if dest.exists() and (expected_size is None or dest.stat().st_size == expected_size):
            return dest
        log(f"  fetch {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "aeoi build_web"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        if expected_size is None or dest.stat().st_size == expected_size:
            return dest
        log(f"  size mismatch on attempt {attempt}: {dest.stat().st_size} != {expected_size}")
        dest.unlink()
    raise SystemExit(f"could not download {url}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def vendor_pyodide() -> list[str]:
    """Runtime + package closure into web/pyodide/; returns the published paths."""
    cache = CACHE / f"pyodide-{PYODIDE_VERSION}"
    lock_path = fetch(PYODIDE_BASE + "pyodide-lock.json", cache / "pyodide-lock.json")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = lock["packages"]
    index = {k.lower().replace("_", "-"): k for k in packages}
    closure: list[str] = []

    def add(name: str) -> None:
        key = index[name.lower().replace("_", "-")]
        if key in closure:
            return
        closure.append(key)
        for dep in packages[key]["depends"]:
            add(dep)

    for name in PYODIDE_PACKAGES:
        add(name)
    out = WEB / "pyodide"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    published = []
    for name in PYODIDE_CORE:
        src = fetch(PYODIDE_BASE + name, cache / name)
        shutil.copy(src, out / name)
        published.append(f"pyodide/{name}")
    for key in closure:
        file_name = packages[key]["file_name"]
        src = fetch(PYODIDE_BASE + file_name, cache / file_name)
        digest = sha256(src)
        if packages[key].get("sha256") and digest != packages[key]["sha256"]:
            raise SystemExit(f"{file_name}: sha256 {digest} != lock {packages[key]['sha256']}")
        shutil.copy(src, out / file_name)
        published.append(f"pyodide/{file_name}")
    pruned = {"info": lock["info"], "packages": {k: packages[k] for k in closure}}
    (out / "pyodide-lock.json").write_text(json.dumps(pruned, indent=1), encoding="utf-8")
    published.append("pyodide/pyodide-lock.json")
    log(f"pyodide {PYODIDE_VERSION}: core + {len(closure)} packages ({', '.join(closure)})")
    return published


def vendor_wheels() -> list[str]:
    """Pure-Python wheels from PyPI into web/wheels/ (pip download, cached)."""
    cache = CACHE / "wheels"
    cache.mkdir(parents=True, exist_ok=True)
    out = WEB / "wheels"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    published = []
    for spec in PYPI_WHEELS:
        name = re.split(r"[=<>!~]", spec, maxsplit=1)[0].lower().replace("-", "_")
        have = sorted(cache.glob(f"{name}-*.whl"))
        if not have or "==" in spec and not any(spec.split("==")[1] in w.name for w in have):
            log(f"  pip download {spec}")
            subprocess.run(
                [sys.executable, "-m", "pip", "download", spec, "--no-deps", "--only-binary=:all:",
                 "--platform", "any", "--python-version", "3.12", "--implementation", "py",
                 "--dest", str(cache), "--quiet"],
                check=True,
            )  # fmt: skip
            have = sorted(cache.glob(f"{name}-*.whl"))
        wheel = [w for w in have if "==" not in spec or spec.split("==")[1] in w.name][-1]
        shutil.copy(wheel, out / wheel.name)
        published.append(f"wheels/{wheel.name}")
    log(f"wheels: {', '.join(p.split('/')[-1] for p in published)}")
    return published


def copy_aeoi_wheel() -> str:
    wheels = sorted((ROOT / "dist").glob("aeoi-*-py3-none-any.whl"))
    if not wheels:
        raise SystemExit("no wheel in dist/: run python -m build first")
    wheel = wheels[-1]
    for old in WEB.glob("aeoi-*.whl"):
        old.unlink()
    shutil.copy(wheel, WEB / wheel.name)
    return wheel.name


def patch_app(aeoi_wheel: str, wheels: list[str]) -> None:
    page = WEB / "app.js"
    text = page.read_text(encoding="utf-8")
    text, n1 = re.subn(r'const WHEEL = "aeoi-[^"]+\.whl";', f'const WHEEL = "{aeoi_wheel}";', text)
    names = ", ".join(f'"{p}"' for p in wheels)
    text, n2 = re.subn(r"const WHEELS = \[[^\]]*\];", f"const WHEELS = [{names}];", text)
    if n1 != 1 or n2 != 1:
        raise SystemExit("WHEEL / WHEELS constants not found in web/app.js")
    page.write_text(text, encoding="utf-8")


def write_service_worker(assets: list[str]) -> None:
    template = (ROOT / "tools" / "sw.template.js").read_text(encoding="utf-8")
    listing = {a: sha256(WEB / a) for a in assets}
    version = hashlib.sha256(json.dumps(listing, sort_keys=True).encode()).hexdigest()[:12]
    sw = template.replace("__VERSION__", version).replace(
        "__ASSETS__", json.dumps(["./", *assets], indent=1)
    )
    (WEB / "sw.js").write_text(sw, encoding="utf-8")
    (WEB / "vendor.json").write_text(
        json.dumps({"version": version, "pyodide": PYODIDE_VERSION, "files": listing}, indent=1),
        encoding="utf-8",
    )
    total = sum((WEB / a).stat().st_size for a in assets)
    log(f"sw.js: cache aeoi-{version}, {len(assets) + 1} entries, {total / 1e6:.1f} MB")


TEMPLATE_LANGS = ("de", "fr", "it", "en")


def write_templates() -> list[str]:
    """The empty Excel template in every language as a static download (web/vorlage/), so the
    home page and the pilot letter can link it without loading the runtime first."""
    from aeoi.crs import template

    out = WEB / "vorlage"
    out.mkdir(exist_ok=True)
    files = []
    for lang in TEMPLATE_LANGS:
        name = f"vorlage/meldbar-vorlage-{lang}.xlsx"
        template.write_template(WEB / name, lang=lang)
        files.append(name)
    log(f"templates: {', '.join(files)}")
    return files


def main() -> int:
    aeoi_wheel = copy_aeoi_wheel()
    pyodide_files = vendor_pyodide()
    wheels = vendor_wheels()
    templates = write_templates()
    patch_app(aeoi_wheel, wheels)
    write_service_worker([*STATIC, *templates, aeoi_wheel, *pyodide_files, *wheels])
    log(f"web/ ready: one origin, no external host ({aeoi_wheel})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
