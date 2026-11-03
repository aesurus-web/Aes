"""Generate the Kreova logo set (SVG with outlined text + PNG exports).

Usage:  python3 brand/kreova/build_logo.py
Requires: fonttools, uharfbuzz, and the Inter Display Bold font.
"""
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
INK = "#141414"
ACCENT = "#FF5A36"
WHITE = "#FFFFFF"
TRACKING = -0.025  # em
OUT = Path(__file__).parent

font = TTFont(FONT)
gs = font.getGlyphSet()
UPM = font["head"].unitsPerEm
blob = hb.Blob.from_file_path(FONT)
hbfont = hb.Font(hb.Face(blob))


def text_path(text, size, x, baseline):
    """Return (svg path d, advance width, ink bounds) for text at size px."""
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    s = size / UPM
    order = font.getGlyphOrder()
    pen = SVGPathPen(gs)
    bpen = BoundsPen(gs)
    cx = 0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        t = (s, 0, 0, -s, x + (cx + pos.x_offset) * s, baseline - pos.y_offset * s)
        gs[name].draw(TransformPen(pen, t))
        gs[name].draw(TransformPen(bpen, t))
        cx += pos.x_advance + (TRACKING * UPM if i < n - 1 else 0)
    return pen.getCommands(), cx * s, bpen.bounds


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}">\n{body}\n</svg>\n')


def fmt(v):
    return f"{v:.2f}"


SIZE = 200          # wordmark font size (px)
PAD = 40
x_height = font["OS/2"].sxHeight * SIZE / UPM
cap = font["OS/2"].sCapHeight * SIZE / UPM

files = {}

# Measure wordmark once
_, adv, (x0, y0, x1, y1) = text_path("kreova", SIZE, 0, 0)
asc = -y0  # height of 'k' above baseline


def wordmark(color, dot=None):
    d, _, b = text_path("kreova", SIZE, PAD - x0, PAD + asc)
    w_ink = b[2]
    body = f'  <path fill="{color}" d="{d}"/>'
    width = w_ink + PAD
    if dot:
        r = SIZE * 0.075
        cx = w_ink + SIZE * 0.035 + r
        cy = PAD + asc - r
        body += f'\n  <circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{dot}"/>'
        width = cx + r + PAD
    return svg(width, asc + 2 * PAD, body)


# A · Pure wordmark
files["kreova-a-wordmark.svg"] = wordmark(INK)
files["kreova-a-wordmark-white.svg"] = wordmark(WHITE)
# B · Wordmark with accent dot (primary)
files["kreova-b-wordmark-dot.svg"] = wordmark(INK, ACCENT)
files["kreova-b-wordmark-dot-white.svg"] = wordmark(WHITE, ACCENT)


# C · Circle mark + wordmark
def lockup(color, mark_fg):
    D = asc * 1.42
    R = D / 2
    gap = SIZE * 0.2
    top = PAD
    cy = top + R
    baseline = cy + asc / 2
    # 'k' inside circle
    ks = D * 0.62
    _, _, kb = text_path("k", ks, 0, 0)
    kw, kh = kb[2] - kb[0], kb[3] - kb[1]
    kd, _, _ = text_path("k", ks, PAD + R - kw / 2 - kb[0], cy + kh / 2 - kb[3])
    wx = PAD + D + gap
    d, _, b = text_path("kreova", SIZE, wx - x0, baseline)
    body = (f'  <circle cx="{fmt(PAD + R)}" cy="{fmt(cy)}" r="{fmt(R)}" fill="{color}"/>\n'
            f'  <path fill="{mark_fg}" d="{kd}"/>\n'
            f'  <path fill="{color}" d="{d}"/>')
    return svg(b[2] + PAD, D + 2 * PAD, body)


files["kreova-c-lockup.svg"] = lockup(INK, WHITE)
files["kreova-c-lockup-white.svg"] = lockup(WHITE, INK)


# D · Icon only (social / app)
def icon(bg, fg, border=None, size=512):
    rx = size * 0.22
    ks = size * 0.68
    _, _, kb = text_path("k", ks, 0, 0)
    kw, kh = kb[2] - kb[0], kb[3] - kb[1]
    r = ks * 0.075
    gap = ks * 0.035
    group_w = kw + gap + 2 * r
    kx = (size - group_w) / 2 - kb[0]
    base = (size + kh) / 2 - kb[3]
    kd, _, b = text_path("k", ks, kx, base)
    stroke = f' stroke="{border}" stroke-width="{size*0.008:.2f}"' if border else ""
    inset = size * 0.004 if border else 0
    body = (f'  <rect x="{fmt(inset)}" y="{fmt(inset)}" width="{fmt(size-2*inset)}" '
            f'height="{fmt(size-2*inset)}" rx="{fmt(rx)}" fill="{bg}"{stroke}/>\n'
            f'  <path fill="{fg}" d="{kd}"/>\n'
            f'  <circle cx="{fmt(b[2] + gap + r)}" cy="{fmt(base - r)}" r="{fmt(r)}" fill="{ACCENT}"/>')
    return svg(size, size, body)


files["kreova-d-icon-dark.svg"] = icon(INK, WHITE)
files["kreova-d-icon-light.svg"] = icon(WHITE, INK, border="#E6E6E6")

svgdir = OUT / "svg"
svgdir.mkdir(exist_ok=True)
for name, content in files.items():
    (svgdir / name).write_text(content)
    print("wrote", svgdir / name)
