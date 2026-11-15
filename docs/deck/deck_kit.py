"""Shared building blocks for the PixelDrex decks: 1920x1080 slides as absolutely positioned HTML with inline PNG
assets, in the format Adobe Express imports (one .slide per page, hz:* canvas metadata)."""

import base64
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = HERE / "assets"
W, H = 1920, 1080

C = {
    "bg": "#0d0f1a",
    "panel": "#161a2b",
    "panel2": "#1d2238",
    "line": "#2b3254",
    "text": "#e8ebf7",
    "muted": "#9aa2c2",
    "yellow": "#ffcc33",
    "teal": "#4fd1c5",
    "pink": "#ff5d8f",
    "green": "#5ee08a",
}
TITLE = "'lores-9-narrow', sans-serif"
DOT = "'dotgothic16', sans-serif"
BODY = "'aileron', sans-serif"


def img(name: str) -> str:
    return "data:image/png;base64," + base64.b64encode((A / name).read_bytes()).decode()


def box(x, y, w, h, inner="", style=""):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">{inner}</div>'


def text(x, y, w, t, size, font=BODY, color=None, weight=400, lh=1.25, extra=""):
    color = color or C["text"]
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font-family:{font};font-size:{size}px;'
        f'font-weight:{weight};line-height:{lh};color:{color};{extra}">{t}</div>'
    )


def picture(x, y, w, h, name, alt, border=True):
    b = f"border:4px solid {C['line']};" if border else ""
    return (
        f'<img src="{img(name)}" alt="{escape(alt)}" width="{w}" height="{h}" '
        f'style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:10px;{b}">'
    )


def panel(x, y, w, h):
    return box(x, y, w, h, style=f"background:{C['panel']};border:2px solid {C['line']};border-radius:18px;")


def kicker(t, x=110, y=86, color=None):
    return text(x, y, 1700, t, 30, DOT, color or C["teal"], extra="letter-spacing:2px;")


def title(t, x=110, y=130, size=104, color=None, w=1700):
    return text(x, y, w, t, size, TITLE, color or C["yellow"], 700, 1.0)


def footer(n, total=8):
    return text(110, 1010, 900, "PIXELDREX · every pixel is a decision", 22, DOT, C["muted"]) + text(
        1610, 1010, 200, f"{n} / {total}", 22, DOT, C["muted"], extra="text-align:right;"
    )


def slide(n, inner, total=8):
    return (
        f'<section class="slide" data-canvas-width="{W}" data-canvas-height="{H}" '
        f'style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{C["bg"]};">'
        f"{inner}{footer(n, total)}</section>"
    )


def stat(x, y, w, value, label, color=None):
    return (
        panel(x, y, w, 150)
        + text(x + 28, y + 22, w - 56, value, 56, TITLE, color or C["yellow"], 700, 1.0)
        + text(x + 28, y + 92, w - 56, label, 24, BODY, C["muted"])
    )


def mono(x, y, w, lines, size=28, h=None):
    body = "<br>".join(lines)
    h = h or (len(lines) * size * 1.45 + 56)
    return panel(x, y, w, h) + text(x + 32, y + 26, w - 64, body, size, DOT, C["text"], 400, 1.45)


def page(slides: list[str], page_title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width={W}">
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="{W}">
<meta name="hz:canvas-height" content="{H}">
<title>{page_title}</title>
<link rel="stylesheet" href="https://use.typekit.net/hcb0fer.css">
<style>
  html, body {{ margin: 0; padding: 0; background: #05060c; }}
  .slide {{ margin: 0 auto 40px; }}
  .slide b {{ color: {C["yellow"]}; font-weight: 700; }}
</style>
</head>
<body>
{chr(10).join(slides)}
</body>
</html>
"""
