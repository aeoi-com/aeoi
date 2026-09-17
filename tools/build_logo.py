"""Build the meldbar logo assets from the bundled Inter font (no font dependency in the SVGs).

    python tools/build_logo.py

Writes into web/:
  logo.svg           horizontal lockup: mark + wordmark + tagline (text as paths)
  logo-mark.svg      the mark alone, transparent background (favicon, inline use)
  icon.svg           PWA icon "any": mark on a rounded light tile
  icon-maskable.svg  PWA icon "maskable": mark inside the 80 % safe zone on a solid tile

The mark: three slanted sheets stacked on the diagonal - the Excel rows that become one file that
goes out - in deep blue, blue and the site's teal. Colours are the tokens below; change them here.
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

NAVY = "#12305b"  # wordmark
MUTED = "#5c6773"  # tagline (site token --muted)
SHEET_TOP = "#1c4f9e"
SHEET_MID = "#2b86c9"
SHEET_BOTTOM = "#13a89e"  # site token --accent-2
TILE_LIGHT = "#f4f6f8"  # site token --bg
TILE_DARK = "#12305b"

WORDMARK = "meldbar"
TAGLINE = "From Excel to XML. Securely."


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


def mark(x: float, y: float, s: float) -> str:
    """Three slanted sheets in a box of side `s` at (x, y)."""

    # geometry in a 64-unit box: sheets 40 wide, 13 high, skewed, stacked with a diagonal offset
    def sheet(ox: float, oy: float, colour: str) -> str:
        w, h, r, k = 37.0, 17.0, 4.0, 12.0  # width, height, corner radius, horizontal skew
        pts = [(ox + k, oy), (ox + k + w, oy), (ox + w, oy + h), (ox, oy + h)]
        # rounded parallelogram via quadratic corners
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
        d = (
            f"M{x0 + r:.2f},{y0:.2f} L{x1 - r:.2f},{y1:.2f} Q{x1:.2f},{y1:.2f} {x1 - r * 0.6:.2f},{y1 + r * 0.8:.2f} "
            f"L{x2 + r * 0.6:.2f},{y2 - r * 0.8:.2f} Q{x2:.2f},{y2:.2f} {x2 - r:.2f},{y2:.2f} "
            f"L{x3 + r:.2f},{y3:.2f} Q{x3:.2f},{y3:.2f} {x3 + r * 0.6:.2f},{y3 - r * 0.8:.2f} "
            f"L{x0 - r * 0.6:.2f},{y0 + r * 0.8:.2f} Q{x0:.2f},{y0:.2f} {x0 + r:.2f},{y0:.2f} Z"
        )
        return f'<path d="{d}" fill="{colour}"/>'

    inner = sheet(14, 5, SHEET_TOP) + sheet(9, 21, SHEET_MID) + sheet(4, 37, SHEET_BOTTOM)
    f = s / 64.0
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({f:.4f})">{inner}</g>'


def build() -> None:
    word_d, word_w = text_path(WORDMARK, 700, 44, letter_spacing=-0.6)
    tag_d, tag_w = text_path(TAGLINE, 500, 15, letter_spacing=0.1)

    # lockup: mark 64px, gap 16, wordmark baseline 44, tagline baseline 68
    mark_size, gap = 64.0, 18.0
    text_x = mark_size + gap
    width = text_x + max(word_w, tag_w) + 4
    height = 76.0
    lockup = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}" role="img" aria-label="meldbar - {TAGLINE}">'
        f"{mark(0, 6, mark_size)}"
        f'<path transform="translate({text_x:.2f},44)" d="{word_d}" fill="{NAVY}"/>'
        f'<path transform="translate({text_x + 1:.2f},68)" d="{tag_d}" fill="{MUTED}"/>'
        "</svg>"
    )
    (WEB / "logo.svg").write_text(lockup, encoding="utf-8")

    mark_only = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="meldbar">'
        f"{mark(0, 0, 64)}</svg>"
    )
    (WEB / "logo-mark.svg").write_text(mark_only, encoding="utf-8")

    icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{TILE_LIGHT}"/>'
        f"{mark(6, 6, 52)}</svg>"
    )
    (WEB / "icon.svg").write_text(icon, encoding="utf-8")

    maskable = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" fill="{TILE_DARK}"/>'
        f"{mark(13, 13, 38)}</svg>"
    )
    (WEB / "icon-maskable.svg").write_text(maskable, encoding="utf-8")
    print(f"logo.svg {width:.0f}x{height:.0f}, logo-mark.svg, icon.svg, icon-maskable.svg written")


if __name__ == "__main__":
    build()
