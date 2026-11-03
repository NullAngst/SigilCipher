#!/usr/bin/env python3
"""Build the Sigil Cipher font from stroke definitions.

Copyright 2026 NullAngst. Licensed under CC BY-ND 4.0, see LICENSE.

Every glyph is drawn on a 14x14 grid running from -7 to 7, with y pointing
down (the same grid the profile-picture seals use). The strokes get turned
into filled outlines with shapely, then written into a TrueType font with
fontTools.

Usage:
    python3 build_font.py [output_dir] [--specimen]
"""
import math
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampNow
from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely.geometry import LineString, LinearRing, MultiPolygon, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

FAMILY = "Sigil Cipher"
VERSION = "1.001"
COPYRIGHT = "Copyright 2026 NullAngst"
LICENSE = ("Licensed under CC BY-ND 4.0. Free to use, copy and share anywhere, "
           "including commercially, with credit. Modified versions may not be shared.")
LICENSE_URL = "https://creativecommons.org/licenses/by-nd/4.0/"

UPM = 1000
SCALE = 50          # font units per grid unit: the -7..7 box becomes 700 units
SIDE = 110          # left and right side bearing
ADVANCE = 14 * SCALE + 2 * SIDE
SPACE = ADVANCE // 2
CAP = 14 * SCALE    # glyphs sit from y=0 up to y=700

WEIGHTS = {"Regular": 1.6, "Bold": 2.6}   # stroke width in grid units


def L(*pts):
    """Open polyline."""
    return ("line", pts)


def F(*pts):
    """Open polyline with flat ends, for marks that stop on another stroke."""
    return ("flatline", pts)


def Z(*pts):
    """Closed polygon outline."""
    return ("ring", pts)


def C(cx, cy, r):
    """Circle outline."""
    return ("circle", (cx, cy, r))


def D(cx, cy, r):
    """Filled dot."""
    return ("dot", (cx, cy, r))


def arc(cx, cy, r, a0, a1, steps=48):
    """Open arc from angle a0 to a1 in degrees, screen coordinates."""
    out = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return ("line", tuple(out))


BOX = Z((-5, -5), (5, -5), (5, 5), (-5, 5))

GLYPHS = {
    # Letters already used on the seal rings. Do not change these, or the
    # existing NULL ANGST and 35 RUINS bands stop matching the font.
    "A": [Z((0, -7), (6, 6), (-6, 6))],
    "G": [C(0, 0, 5), L((-7, 0), (7, 0))],
    "I": [L((0, -7), (0, 7)), L((-4, 3), (4, -3))],
    "L": [L((-6, -7), (6, -7)), L((-6, -2), (0, 7), (6, -2))],
    "N": [C(0, -4, 3), L((0, -1), (0, 7)), L((-5, 7), (5, 7))],
    "R": [L((-5, 7), (-5, -7), (6, -3), (-5, 1))],
    "S": [L((-6, -7), (6, -2), (-6, 2), (6, 7))],
    "T": [L((0, -1), (0, 7)), L((-6, -7), (0, -1), (6, -7))],
    "U": [L((-6, -7), (-6, 7), (6, 7), (6, -7)), L((0, -3), (0, 7))],
    "3": [L((-6, -6), (6, -6)), L((-6, 0), (6, 0)), L((-6, 6), (6, 6))],
    "5": [BOX, F((-5, 5), (5, -5))],

    # New letters. Most come in pairs that mirror or invert an existing one:
    # A/D, P/Q, U/H, L/V, T/Y, N/J, M/W.
    "B": [C(-3.8, 0, 2.8), C(3.8, 0, 2.8), L((0, -7), (0, 7))],
    "C": [arc(0, 0, 6, 40, 320)],
    "D": [Z((-6, -6), (6, -6), (0, 7))],
    "E": [C(0, 0, 6), D(0, 0, 1.6)],
    "F": [L((0, -7), (0, 7)), L((-5, -1), (5, -5)), L((-5, 5), (5, 1))],
    "H": [L((-6, 7), (-6, -7), (6, -7), (6, 7)), L((0, 3), (0, -7))],
    "J": [L((0, -7), (0, 1)), C(0, 4, 3)],
    "K": [L((6, -7), (-6, 0), (6, 7)), D(2.5, 0, 1.6)],
    "M": [L((-7, 6), (-3.5, -6), (0, 6), (3.5, -6), (7, 6))],
    "O": [C(0, 0, 6)],
    "P": [Z((-6, -6), (6, 0), (-6, 6))],
    "Q": [Z((6, -6), (-6, 0), (6, 6))],
    "V": [L((-6, 2), (0, -7), (6, 2)), L((-6, 7), (6, 7))],
    "W": [L((-7, -6), (-3.5, 6), (0, -6), (3.5, 6), (7, -6))],
    "X": [L((-6, -7), (6, 7)), L((6, -7), (-6, 7))],
    "Y": [L((0, -7), (0, 1)), L((-6, 7), (0, 1), (6, 7))],
    "Z": [L((-6, -6), (6, -6)), L((-6, 6), (6, 6)), C(0, 0, 2.5)],

    # Digits: 1 to 4 are stacked bars (3 already was), 0 and 5 to 9 are
    # boxes with a different mark inside.
    "0": [BOX],
    "1": [L((-6, 0), (6, 0))],
    "2": [L((-6, -3), (6, -3)), L((-6, 3), (6, 3))],
    "4": [L((-6, -6), (6, -6)), L((-6, -2), (6, -2)),
          L((-6, 2), (6, 2)), L((-6, 6), (6, 6))],
    "6": [BOX, F((-5, 5), (5, -5)), F((-5, -5), (5, 5))],
    "7": [BOX, F((0, -5), (0, 5))],
    "8": [BOX, F((-5, 0), (5, 0))],
    "9": [BOX, D(0, 0, 1.6)],

    # Separators from the seal rings, plus a few basics.
    ".": [D(0, 0, 1.4)],
    "|": [Z((0, -7), (6, 0), (0, 7), (-6, 0))],
    "-": [L((-3, 0), (3, 0))],
    ",": [D(0, 4, 1.4)],
    ":": [D(0, -3, 1.4), D(0, 3, 1.4)],
}

NAMES = {".": "period", "|": "bar", "-": "hyphen", ",": "comma", ":": "colon",
         "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
         "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}


def to_font(x, y):
    """Grid coordinates (y down) to font units (y up)."""
    return (SIDE + (x + 7) * SCALE, (7 - y) * SCALE)


def outline(parts, stroke):
    half = stroke * SCALE / 2
    shapes = []
    for kind, data in parts:
        if kind == "line":
            shapes.append(LineString([to_font(*p) for p in data]).buffer(
                half, cap_style="square", join_style="mitre", mitre_limit=4))
        elif kind == "flatline":
            shapes.append(LineString([to_font(*p) for p in data]).buffer(
                half, cap_style="flat", join_style="mitre", mitre_limit=4))
        elif kind == "ring":
            shapes.append(LinearRing([to_font(*p) for p in data]).buffer(
                half, join_style="mitre", mitre_limit=4))
        elif kind == "circle":
            cx, cy, r = data
            shapes.append(Point(to_font(cx, cy)).buffer(r * SCALE + half, 64)
                          .difference(Point(to_font(cx, cy)).buffer(r * SCALE - half, 64)))
        elif kind == "dot":
            cx, cy, r = data
            shapes.append(Point(to_font(cx, cy)).buffer(r * SCALE, 32))
    merged = unary_union(shapes)
    if isinstance(merged, Polygon):
        merged = MultiPolygon([merged])
    return [orient(p, sign=-1.0) for p in merged.geoms]


def draw(pen, polys):
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = []
            for x, y in list(ring.coords)[:-1]:
                p = (round(x), round(y))
                if not pts or pts[-1] != p:
                    pts.append(p)
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts.pop()
            if len(pts) < 3:
                continue
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()


def build(style, stroke, out_dir):
    order = [".notdef", "space"]
    cmap = {32: "space"}
    glyphs = {}

    pen = TTGlyphPen(None)
    pen.moveTo((SIDE, 0)); pen.lineTo((SIDE, CAP))
    pen.lineTo((ADVANCE - SIDE, CAP)); pen.lineTo((ADVANCE - SIDE, 0)); pen.closePath()
    pen.moveTo((SIDE + 60, 60)); pen.lineTo((ADVANCE - SIDE - 60, 60))
    pen.lineTo((ADVANCE - SIDE - 60, CAP - 60)); pen.lineTo((SIDE + 60, CAP - 60)); pen.closePath()
    glyphs[".notdef"] = pen.glyph()
    glyphs["space"] = TTGlyphPen(None).glyph()

    for ch, parts in GLYPHS.items():
        name = NAMES.get(ch, ch)
        pen = TTGlyphPen(None)
        draw(pen, outline(parts, stroke))
        glyphs[name] = pen.glyph()
        order.append(name)
        cmap[ord(ch)] = name
        if ch.isalpha():
            cmap[ord(ch.lower())] = name    # lowercase types the same sigil

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    glyf = fb.font["glyf"]
    metrics = {}
    for n in order:
        g = glyf[n]
        g.recalcBounds(glyf)
        width = SPACE if n == "space" else ADVANCE
        metrics[n] = (width, getattr(g, "xMin", 0) if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=850, descent=-200)
    fb.setupNameTable({
        "copyright": COPYRIGHT,
        "licenseDescription": LICENSE,
        "licenseInfoURL": LICENSE_URL,
        "familyName": FAMILY,
        "styleName": style,
        "uniqueFontIdentifier": f"{FAMILY.replace(' ', '')}-{style}-{VERSION}",
        "fullName": f"{FAMILY} {style}",
        "psName": f"{FAMILY.replace(' ', '')}-{style}",
        "version": f"Version {VERSION}",
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-200, sTypoLineGap=0,
                usWinAscent=900, usWinDescent=250, sCapHeight=CAP, sxHeight=CAP,
                usWeightClass=700 if style == "Bold" else 400,
                fsSelection=0x20 if style == "Bold" else 0x40)
    fb.setupPost()
    now = timestampNow()
    fb.setupHead(unitsPerEm=UPM, macStyle=1 if style == "Bold" else 0,
                 created=now, modified=now)

    base = out_dir / f"{FAMILY.replace(' ', '')}-{style}"
    fb.save(f"{base}.ttf")
    try:
        import brotli  # noqa: F401  (woff2 needs it)
        fb.font.flavor = "woff2"
        fb.font.save(f"{base}.woff2")
    except ImportError:
        print("brotli not installed, skipping .woff2", file=sys.stderr)
    return f"{base}.ttf"


def specimen(ttf_regular, ttf_bold, path):
    """Key grid: every sigil with the character it types, then sample words."""
    from PIL import Image, ImageDraw, ImageFont
    chars = sorted(GLYPHS, key=lambda c: (not c.isalpha(), not c.isdigit(), c))
    cols, cell = 9, 150
    rows = -(-len(chars) // cols)
    samples = ["|NULL.ANGST|", "|35.RUINS|", "TRSTS"]
    w, h = cols * cell + 80, rows * cell + 60 + len(samples) * 130 + 40
    img = Image.new("RGB", (w, h), "#0b0b0b")
    d = ImageDraw.Draw(img)
    sig = ImageFont.truetype(ttf_regular, 80)
    bold = ImageFont.truetype(ttf_bold, 72)
    label = ImageFont.load_default(size=24)
    for i, ch in enumerate(chars):
        x = 40 + (i % cols) * cell
        y = 30 + (i // cols) * cell
        d.text((x + cell // 2, y + 55), ch, font=sig, fill="#e4e4e4", anchor="mm")
        d.text((x + cell // 2, y + 118), ch, font=label, fill="#8a8a8a", anchor="mm")
    y = 30 + rows * cell + 30
    for text in samples:
        d.text((40, y), text, font=bold, fill="#e4e4e4")
        d.text((40, y + 88), text, font=label, fill="#8a8a8a")
        y += 130
    img.save(path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path(args[0] if args else "fonts")
    out_dir.mkdir(parents=True, exist_ok=True)
    built = {style: build(style, w, out_dir) for style, w in WEIGHTS.items()}
    for path in built.values():
        print(f"built {path}")
    if "--specimen" in sys.argv:
        specimen(built["Regular"], built["Bold"], out_dir / "specimen.png")
        print(f"built {out_dir / 'specimen.png'}")


if __name__ == "__main__":
    main()
