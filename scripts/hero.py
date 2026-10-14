"""Compose the README's hero image — pixels in, paths out.

Not shipped code. Writes docs/hero.svg, then rasterises it to docs/hero.png with a
headless Chromium (the README shows the PNG: GitHub's `<img>` view of an SVG loads
no fonts). Needs the Inter and DejaVu Sans Mono fonts and Pillow (which also
pixelates the left-hand picture, so both halves are the same drawing).

Same drafting-sheet family as the author's other repos, in the app's own colors
and with its logo mark (public/favicon.svg). No version or counts on it.

Usage, from the repository root:

    make hero
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_SVG = ROOT / "docs" / "hero.svg"
OUT_PNG = ROOT / "docs" / "hero.png"

#: The GitHub social-preview size, which the README shows scaled to its column.
W, H = 1280, 640

GROUND = "#171b1f"  # the og image's
GRID = "#1f252b"
INK = "#eef2f5"
SOFT = "#c3ccd4"
DIM = "#8b96a1"
FRAME = "#465260"
PANEL = "#1e242a"
TEAL = "#34c9bb"  # the app's accent, dark theme
SANS = "Inter, 'DejaVu Sans', sans-serif"
DISPLAY = "'Inter Display', Inter, sans-serif"
MONO = "'DejaVu Sans Mono', monospace"

#: The picture both halves draw: a four-colour landscape, in a 338 x 234 box.
SKY, SUN, BACK, FRONT = "#bfe9e3", "#f4b942", "#2b6f78", "#0e8f86"
PW, PH = 338, 234


def text(
    x: float,
    y: float,
    s: str,
    *,
    size: float,
    fill: str = INK,
    family: str = SANS,
    weight: int = 400,
    anchor: str = "start",
    spacing: float = 0,
    italic: bool = False,
) -> str:
    style = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'letter-spacing="{spacing}"{style} xml:space="preserve">{escape(s)}</text>'
    )


def sheet() -> list[str]:
    """Grid, border with zone marks, registration marks — the family's drafting sheet."""
    out = [f'<rect width="{W}" height="{H}" fill="{GROUND}"/>']
    for x in range(0, W, 20):
        width = 0.9 if x % 100 == 0 else 0.4
        out.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{GRID}" stroke-width="{width}"/>'
        )
    for y in range(0, H, 20):
        width = 0.9 if y % 100 == 0 else 0.4
        out.append(
            f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{GRID}" stroke-width="{width}"/>'
        )
    out.append(
        f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" fill="none" stroke="{GRID}"/>'
    )
    out.append(
        f'<rect x="30" y="30" width="{W - 60}" height="{H - 60}" fill="none" '
        f'stroke="{FRAME}" stroke-width="1.5"/>'
    )
    zw = (W - 60) / 8
    for i in range(8):
        x = 30 + zw * i
        if i:
            out.append(f'<line x1="{x}" y1="16" x2="{x}" y2="30" stroke="{FRAME}"/>')
            out.append(
                f'<line x1="{x}" y1="{H - 30}" x2="{x}" y2="{H - 16}" stroke="{FRAME}"/>'
            )
        for y in (27, H - 19):
            out.append(
                text(
                    x + zw / 2,
                    y,
                    str(8 - i),
                    size=9,
                    fill=DIM,
                    family=MONO,
                    anchor="middle",
                )
            )
    zh = (H - 60) / 4
    for i in range(4):
        y = 30 + zh * i
        if i:
            out.append(f'<line x1="16" y1="{y}" x2="30" y2="{y}" stroke="{FRAME}"/>')
            out.append(
                f'<line x1="{W - 30}" y1="{y}" x2="{W - 16}" y2="{y}" stroke="{FRAME}"/>'
            )
        for x in (23, W - 23):
            out.append(
                text(
                    x,
                    y + zh / 2 + 3,
                    "ABCD"[i],
                    size=9,
                    fill=DIM,
                    family=MONO,
                    anchor="middle",
                )
            )
    for cx, cy in ((48, 48), (48, H - 48)):
        out += [
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{TEAL}"/>',
            f'<line x1="{cx - 11}" y1="{cy}" x2="{cx + 11}" y2="{cy}" stroke="{TEAL}"/>',
            f'<line x1="{cx}" y1="{cy - 11}" x2="{cx}" y2="{cy + 11}" stroke="{TEAL}"/>',
        ]
    return out


def mark(x: float, y: float, size: float) -> str:
    """The app's logo mark: a Bézier curve between two square anchor handles."""
    k = size / 40
    return (
        f'<g transform="translate({x},{y}) scale({k})">'
        f'<path d="M9 27 C 21 27, 13 13, 31 13" fill="none" stroke="{TEAL}" '
        'stroke-width="2.4" stroke-linecap="round"/>'
        f'<rect x="5.5" y="23.5" width="7" height="7" rx="1.3" fill="{TEAL}"/>'
        f'<rect x="27.5" y="9.5" width="7" height="7" rx="1.3" fill="{TEAL}"/></g>'
    )


def wordmark() -> list[str]:
    return [
        mark(52, 40, 104),
        f'<text x="166" y="118" font-family="{DISPLAY}" font-size="70" font-weight="800" '
        f'letter-spacing="-1.5"><tspan fill="{INK}">Image to </tspan>'
        f'<tspan fill="{TEAL}">SVG</tspan></text>',
        text(68, 176, "Free · private · no ads.", size=25, fill=SOFT),
        text(
            68,
            204,
            "Any image to a clean vector, right in your browser. Nothing is uploaded.",
            size=15,
            fill=DIM,
        ),
    ]


def title_block() -> list[str]:
    x, y, w, h = 842, 62, 376, 64
    half = w / 2 - 20
    cells = [
        (0.0, "RUNS IN", "your browser, offline too"),
        (half + 30, "TRACER", "VTracer · WASM"),
    ]
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{GROUND}" stroke="{FRAME}" '
        f'stroke-width="1.2"/>',
        f'<line x1="{x}" y1="{y + h / 2 + 4}" x2="{x + w}" y2="{y + h / 2 + 4}" stroke="{FRAME}"/>',
        f'<line x1="{x + half + 30}" y1="{y + h / 2 + 4}" x2="{x + half + 30}" y2="{y + h}" '
        f'stroke="{FRAME}"/>',
        text(x + 10, y + 14, "PROJECT", size=8, fill=DIM, family=MONO, spacing=1.5),
        text(x + 10, y + 30, "image-to-svg", size=14, weight=700, family=MONO),
    ]
    for cx, label, value in cells:
        out.append(
            text(x + cx + 10, y + 47, label, size=8, fill=DIM, family=MONO, spacing=1.5)
        )
        out.append(
            text(
                x + cx + 10,
                y + 61,
                value,
                size=11,
                family=MONO,
                fill=TEAL if cx else INK,
            )
        )
    return out


def caption(x: float, y: float, s: str) -> str:
    return text(x, y, s, size=10, fill=TEAL, family=MONO, spacing=2, weight=700)


def pixels(x0: float, y0: float) -> list[str]:
    """The landscape rasterised at 26 x 18 and drawn back as its pixels."""
    cols, rows = 26, 18
    scale = 4
    im = Image.new("RGB", (PW * scale, PH * scale), SKY)
    d = ImageDraw.Draw(im)
    d.ellipse(
        [(250 - 34) * scale, (62 - 34) * scale, (250 + 34) * scale, (62 + 34) * scale],
        fill=SUN,
    )
    d.polygon(
        [(0, PH * scale), (130 * scale, 70 * scale), (270 * scale, PH * scale)],
        fill=BACK,
    )
    d.polygon(
        [
            (110 * scale, PH * scale),
            (232 * scale, 112 * scale),
            (PW * scale, PH * scale),
        ],
        fill=FRONT,
    )
    small = im.resize((cols, rows), Image.Resampling.BOX)
    cw, ch = PW / cols, PH / rows
    out = []
    for j in range(rows):
        for i in range(cols):
            r, g, b = small.getpixel((i, j))[:3]
            out.append(
                f'<rect x="{x0 + i * cw:.2f}" y="{y0 + j * ch:.2f}" width="{cw + 0.3:.2f}" '
                f'height="{ch + 0.3:.2f}" fill="#{r:02x}{g:02x}{b:02x}"/>'
            )
    return out


def vector(x0: float, y0: float) -> list[str]:
    """The same landscape as clean paths, with the pen tool's anchors on one of them."""

    def p(x: float, y: float) -> str:
        return f"{x0 + x},{y0 + y}"

    back = f"M{p(0, PH)} Q{p(70, 120)} {p(130, 70)} Q{p(190, 120)} {p(270, PH)} Z"
    front = f"M{p(110, PH)} Q{p(170, 150)} {p(232, 112)} Q{p(290, 150)} {p(PW, PH)} Z"
    out = [
        f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" fill="{SKY}"/>',
        f'<circle cx="{x0 + 250}" cy="{y0 + 62}" r="34" fill="{SUN}"/>',
        f'<path d="{back}" fill="{BACK}"/>',
        f'<path d="{front}" fill="{FRONT}"/>',
        # The editing overlay: the front ridge's outline, anchors and one handle.
        f'<path d="{front}" fill="none" stroke="#ffffff" stroke-width="1.4" '
        f'stroke-dasharray="4 3"/>',
        f'<line x1="{x0 + 170}" y1="{y0 + 150}" x2="{x0 + 232}" y2="{y0 + 112}" '
        f'stroke="#ffffff" stroke-width="1"/>',
        f'<circle cx="{x0 + 170}" cy="{y0 + 150}" r="4" fill="#ffffff"/>',
    ]
    for ax, ay in ((110, PH), (232, 112), (PW, PH)):
        out.append(
            f'<rect x="{x0 + ax - 5}" y="{y0 + ay - 5}" width="10" height="10" rx="2" '
            f'fill="{GROUND}" stroke="#ffffff" stroke-width="1.6"/>'
        )
    return out


def frame(x: float, y: float, w: float, h: float, label: str, tag: str) -> list[str]:
    return [
        caption(x, y - 12, label),
        f'<rect x="{x - 8}" y="{y - 0}" width="{w + 16}" height="{h + 36}" rx="6" '
        f'fill="{PANEL}" stroke="{FRAME}"/>',
        text(x + w, y + h + 25, tag, size=11.5, family=MONO, fill=DIM, anchor="end"),
    ]


STEPS = [
    ("Upload", "PNG, JPG, WebP, GIF, BMP"),
    ("Edit", "background, fill, scale"),
    ("Trace", "colors · detail · curves"),
    ("Export", "SVG, at full resolution"),
]


def wizard() -> list[str]:
    x, y, w = 492, 262, 296
    out = [caption(x, y - 12, "FOUR STEPS")]
    for i, (name, sub) in enumerate(STEPS):
        sy = y + i * 62
        active = name == "Trace"
        out += [
            f'<rect x="{x}" y="{sy}" width="{w}" height="46" rx="23" '
            f'fill="{"#123a37" if active else PANEL}" stroke="{TEAL if active else FRAME}" '
            f'stroke-width="{1.6 if active else 1}"/>',
            f'<circle cx="{x + 24}" cy="{sy + 23}" r="12" fill="{TEAL if active else GROUND}" '
            f'stroke="{TEAL}"/>',
            text(
                x + 24,
                sy + 27.5,
                str(i + 1),
                size=12,
                weight=700,
                family=MONO,
                fill=GROUND if active else TEAL,
                anchor="middle",
            ),
            text(x + 48, sy + 28, name, size=15, weight=700, fill=INK),
            text(
                x + w - 18,
                sy + 28,
                sub,
                size=12,
                fill=SOFT if active else DIM,
                anchor="end",
            ),
        ]
        if i < len(STEPS) - 1:
            out.append(
                f'<line x1="{x + 24}" y1="{sy + 46}" x2="{x + 24}" y2="{sy + 62}" '
                f'stroke="{FRAME}" stroke-width="1.4"/>'
            )
    return out


def arrows() -> list[str]:
    out = []
    for x1, x2 in ((430, 482), (798, 850)):
        out += [
            f'<line x1="{x1}" y1="384" x2="{x2 - 6}" y2="384" stroke="{TEAL}" '
            f'stroke-width="1.6" stroke-dasharray="5 3"/>',
            f'<path d="M{x2 - 9},378 L{x2},384 L{x2 - 9},390" fill="none" stroke="{TEAL}" '
            f'stroke-width="1.6"/>',
        ]
    return out


def strip() -> list[str]:
    items = [
        ("private", "files never leave your device"),
        ("free", "no limits, no sign-up, no ads"),
        ("offline", "installs as an app"),
    ]
    # Clear of the claude-arsenal badge on the frame's bottom edge.
    x0, y, w, h, gap = 64, 546, 376, 40, 9
    out = []
    for i, (name, sub) in enumerate(items):
        x = x0 + i * (w + gap)
        out += [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{PANEL}" '
            f'stroke="{FRAME}" stroke-width="0.8"/>',
            f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{TEAL}"/>',
            text(x + 16, y + 25, name, size=12.5, weight=700, family=MONO, fill=TEAL),
            text(x + 16 + len(name) * 7.6 + 10, y + 25, sub, size=12, fill=SOFT),
        ]
    return out


#: claude-arsenal's own logo, for the "built with" stamp on the frame.
ARSENAL_LOGO = ROOT / "docs" / "claude-arsenal-logo.svg"
#: claude-arsenal's orange (#c4623f), lifted a step so it reads on the dark ground.
ARSENAL = "#e07a45"
#: DejaVu Sans Mono's advance, in em.
MONO_EM = 0.602


def width(s: str, size: float, face: str) -> float:
    """Advance of `s` in an installed face (an fc-match pattern)."""
    path = subprocess.run(
        ["fc-match", "-f", "%{file}", face], capture_output=True, text=True, check=True
    ).stdout
    return float(ImageFont.truetype(path, 100).getlength(s)) * size / 100


def powered_by() -> list[str]:
    """A "built with" badge for claude-arsenal, set on the frame's bottom edge at the right."""
    src = ARSENAL_LOGO.read_text().strip()
    inner = src[src.index(">") + 1 : src.rindex("</svg>")]
    lead, name, url = (
        "built with",
        "claude-arsenal",
        "github.com/nuncaeslupus/claude-arsenal",
    )
    tile, pad, gap = 22, 8, 8
    lead_w = width(lead, 12, "Inter")
    name_w = width(name, 15, "Inter:bold")
    url_w = len(url) * 10 * MONO_EM
    total = pad + tile + gap + lead_w + 6 + name_w + 12 + url_w + pad + 6
    right, cy = W - 30 - 24, H - 30
    x = right - total
    tx = x + pad + tile + gap
    return [
        (
            f'<rect x="{x:.1f}" y="{cy - 16}" width="{total:.1f}" height="32" rx="16" '
            f'fill="{GROUND}" stroke="{ARSENAL}" stroke-width="1.5"/>'
        ),
        (
            f'<svg x="{x + pad:.1f}" y="{cy - tile / 2}" width="{tile}" height="{tile}" '
            f'viewBox="0 0 64 64">{inner}</svg>'
        ),
        text(round(tx, 1), cy + 4.3, lead, size=12, fill=DIM),
        text(
            round(tx + lead_w + 6, 1), cy + 5.3, name, size=15, fill=ARSENAL, weight=700
        ),
        text(
            round(tx + lead_w + 6 + name_w + 12, 1),
            cy + 3.6,
            url,
            size=10,
            fill=DIM,
            family=MONO,
        ),
    ]


def svg() -> str:
    lx, rx, py = 72, 870, 262
    parts = sheet() + wordmark() + title_block()
    parts += frame(lx, py, PW, PH, "THE IMAGE · PIXELS", "photo.png") + pixels(
        lx, py + 8
    )
    parts += frame(rx, py, PW, PH, "THE SVG · PATHS", "photo.svg") + vector(rx, py + 8)
    parts += wizard() + arrows() + strip()
    parts += powered_by()
    body = "\n  ".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n  {body}\n</svg>\n'
    )


def chromium() -> str:
    for candidate in (
        os.environ.get("CHROMIUM"),
        "/opt/pw-browsers/chromium",
        shutil.which("chromium"),
        shutil.which("google-chrome"),
    ):
        if candidate and Path(candidate).exists():
            return candidate
    sys.exit("hero: no Chromium found; set CHROMIUM=/path/to/chrome")


def main() -> None:
    OUT_SVG.write_text(svg())
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "hero.html"
        page.write_text(
            f'<html><body style="margin:0;overflow:hidden">{svg()}</body></html>'
        )
        subprocess.run(
            [
                chromium(),
                "--headless=new",
                "--no-sandbox",
                "--hide-scrollbars",
                "--force-device-scale-factor=2",
                f"--window-size={W},{H + 200}",
                f"--screenshot={OUT_PNG}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    # Headless Chromium's viewport is shorter than its window: shoot tall, then crop.

    with Image.open(OUT_PNG) as shot:
        shot.crop((0, 0, W * 2, H * 2)).save(OUT_PNG, optimize=True)
    print(f"wrote {OUT_SVG.relative_to(ROOT)} and {OUT_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
