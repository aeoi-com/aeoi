"""Build the meldbar logo assets from the bundled Inter font (no font dependency in the SVGs).

    python tools/build_logo.py

Writes into web/:
  logo.svg           horizontal lockup: mark + wordmark + tagline (text as paths)
  logo-mark.svg      the mark alone, transparent background (favicon, inline use)
  icon.svg           PWA icon "any": mark on a rounded light tile
  icon-maskable.svg  PWA icon "maskable": mark inside the 80 % safe zone on the light tile

The mark: four rising bars - the rows of the return - under a check mark: the declaration,
right the first time. Green to teal to navy; the check in navy. Colours are the tokens below.
"""

from __future__ import annotations

import io
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
FONT = WEB / "fonts" / "inter-latin.woff2"

NAVY = "#12305b"  # wordmark, check mark, bar 4 bottom
MUTED = "#5b6b83"  # tagline
BAR_GRADIENTS = [  # top -> bottom colour of the four bars, left to right
    ("#7ccfa8", "#4fbf9f"),
    ("#8ad6ab", "#66c8a2"),
    ("#4dc0a6", "#2ea9b1"),
    ("#265a90", "#12305b"),
]
TILE_LIGHT = "#f4f6f8"  # site token --bg

WORDMARK = "meldbar"
TAGLINE = "YOUR DECLARATION. FIRST TIME RIGHT."


def _instance(weight: int) -> tuple[TTFont, bytes]:
    font = TTFont(FONT)
    inst = instantiateVariableFont(font, {"wght": weight}, inplace=False)
    inst.flavor = None  # plain TTF bytes for harfbuzz
    buf = io.BytesIO()
    inst.save(buf)
    return inst, buf.getvalue()


def text_path(
    text: str, weight: int, size: float, letter_spacing: float = 0.0
) -> tuple[str, float]:
    """SVG path data for `text` at `size` px (baseline at y=0, x from 0) and its advance width."""
    ttf, data = _instance(weight)
    upem = ttf["head"].unitsPerEm
    scale = size / upem
    face = hb.Face(data)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    glyph_set = ttf.getGlyphSet()
    order = ttf.getGlyphOrder()
    pen = SVGPathPen(glyph_set)
    x = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions, strict=True):
        name = order[info.codepoint]
        gx = (x + pos.x_offset) * scale
        gy = pos.y_offset * scale
        tpen = TransformPen(pen, (scale, 0, 0, -scale, gx, -gy))
        glyph_set[name].draw(tpen)
        x += pos.x_advance + letter_spacing / scale
    return pen.getCommands(), x * scale


def mark(x: float, y: float, s: float, uid: str = "m") -> str:
    """Four bars and a check mark in a box of side `s` at (x, y); gradients get ids prefixed `uid`."""
    # geometry in a 64-unit box, measured on the reference artwork
    bars = [
        (0.0, 22.4),
        (18.4, 39.6),
        (36.8, 34.4),
        (55.2, 22.4),
    ]  # (x, top); bottom at 61, width 8.8
    defs = "".join(
        f'<linearGradient id="{uid}{i}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'
        for i, (top, bottom) in enumerate(BAR_GRADIENTS)
    )
    rects = "".join(
        f'<rect x="{bx:.1f}" y="{top:.1f}" width="8.8" height="{61 - top:.1f}" rx="2.2" fill="url(#{uid}{i})"/>'
        for i, (bx, top) in enumerate(bars)
    )
    check = (
        f'<path d="M17.2,15.8 L29.4,28.6 L56.6,2.4" fill="none" stroke="{NAVY}" stroke-width="7.4" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )
    f = s / 64.0
    return f'<defs>{defs}</defs><g transform="translate({x:.2f},{y:.2f}) scale({f:.4f})">{rects}{check}</g>'


def build() -> None:
    word_d, word_w = text_path(WORDMARK, 700, 44, letter_spacing=-0.6)
    tag_d, tag_w = text_path(TAGLINE, 600, 10, letter_spacing=0.9)
    tag_scale = word_w / tag_w  # the tagline spans exactly the wordmark, as in the artwork
    tag_d, tag_w = text_path(TAGLINE, 600, 10 * tag_scale, letter_spacing=0.9 * tag_scale)

    # lockup: mark 64px, gap 16, wordmark baseline 44, tagline baseline 68
    mark_size, gap = 64.0, 18.0
    text_x = mark_size + gap
    width = text_x + max(word_w, tag_w) + 4
    height = 76.0
    lockup = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}" role="img" aria-label="meldbar - {TAGLINE}">'
        f"{mark(0, 6, mark_size, 'l')}"
        f'<path transform="translate({text_x:.2f},44)" d="{word_d}" fill="{NAVY}"/>'
        f'<path transform="translate({text_x + 1:.2f},68)" d="{tag_d}" fill="{MUTED}"/>'
        "</svg>"
    )
    (WEB / "logo.svg").write_text(lockup, encoding="utf-8")

    mark_only = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="meldbar">'
        f"{mark(0, 0, 64, 'k')}</svg>"
    )
    (WEB / "logo-mark.svg").write_text(mark_only, encoding="utf-8")

    icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{TILE_LIGHT}"/>'
        f"{mark(6, 6, 52, 'i')}</svg>"
    )
    (WEB / "icon.svg").write_text(icon, encoding="utf-8")

    maskable = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" fill="{TILE_LIGHT}"/>'
        f"{mark(13, 13, 38, 'a')}</svg>"
    )
    (WEB / "icon-maskable.svg").write_text(maskable, encoding="utf-8")
    print(f"logo.svg {width:.0f}x{height:.0f}, logo-mark.svg, icon.svg, icon-maskable.svg written")


if __name__ == "__main__":
    build()
