"""Build docs/deck/pixeldrex_deck.html: an 8-slide 1920x1080 pitch deck with inline PNG assets (for Adobe Express)."""
import base64
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = HERE / "assets"
W, H = 1920, 1080

C = {"bg": "#0d0f1a", "panel": "#161a2b", "panel2": "#1d2238", "line": "#2b3254", "text": "#e8ebf7",
     "muted": "#9aa2c2", "yellow": "#ffcc33", "teal": "#4fd1c5", "pink": "#ff5d8f", "green": "#5ee08a"}
TITLE = "'lores-9-narrow', sans-serif"
DOT = "'dotgothic16', sans-serif"
BODY = "'aileron', sans-serif"


def img(name: str) -> str:
    return "data:image/png;base64," + base64.b64encode((A / name).read_bytes()).decode()


def box(x, y, w, h, inner="", style=""):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">{inner}</div>'


def text(x, y, w, t, size, font=BODY, color=None, weight=400, lh=1.25, extra=""):
    color = color or C["text"]
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font-family:{font};font-size:{size}px;'
            f'font-weight:{weight};line-height:{lh};color:{color};{extra}">{t}</div>')


def picture(x, y, w, h, name, alt, border=True):
    b = f"border:4px solid {C['line']};" if border else ""
    return (f'<img src="{img(name)}" alt="{escape(alt)}" width="{w}" height="{h}" '
            f'style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:10px;{b}">')


def panel(x, y, w, h):
    return box(x, y, w, h, style=f"background:{C['panel']};border:2px solid {C['line']};border-radius:18px;")


def kicker(t, x=110, y=86, color=None):
    return text(x, y, 1700, t, 30, DOT, color or C["teal"], extra="letter-spacing:2px;")


def title(t, x=110, y=130, size=104, color=None, w=1700):
    return text(x, y, w, t, size, TITLE, color or C["yellow"], 700, 1.0)


def footer(n):
    return (text(110, 1010, 900, "PIXELDREX · every pixel is a decision", 22, DOT, C["muted"]) +
            text(1610, 1010, 200, f"{n} / 8", 22, DOT, C["muted"], extra="text-align:right;"))


def slide(n, inner):
    return (f'<section class="slide" data-canvas-width="{W}" data-canvas-height="{H}" '
            f'style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{C["bg"]};">'
            f'{inner}{footer(n)}</section>')


def stat(x, y, w, value, label, color=None):
    return (panel(x, y, w, 150) +
            text(x + 28, y + 22, w - 56, value, 56, TITLE, color or C["yellow"], 700, 1.0) +
            text(x + 28, y + 92, w - 56, label, 24, BODY, C["muted"]))


def mono(x, y, w, lines, size=28, h=None):
    body = "<br>".join(lines)
    h = h or (len(lines) * size * 1.45 + 56)
    return (panel(x, y, w, h) + text(x + 32, y + 26, w - 64, body, size, DOT, C["text"], 400, 1.45))


S = []

# 1 — title
S.append(slide(1,
    kicker("DREXATHON · WILDCARD TRACK · NOV 14 2026") +
    text(110, 190, 960, "PIXELDREX", 150, TITLE, C["yellow"], 700, 1.0) +
    text(110, 400, 960, "GIFs made entirely of decisions.", 56, BODY, C["text"], 700) +
    text(110, 500, 860, "Drex can't draw. It only answers multiple-choice questions — so every pixel of every "
                        "frame is a question, and the answers become animated GIFs.", 36, BODY, C["muted"], 400, 1.4) +
    text(110, 800, 900, "github.com/mauryantitans/PixelDrex", 32, DOT, C["teal"]) +
    picture(1170, 150, 620, 620, "hero_fire.png", "forest fire painted by Drex") +
    text(1170, 800, 620, "A forest fire nobody animated: 41,984 Drex decisions, 22 seconds, under 2¢.", 26, BODY,
         C["muted"], 400, 1.35)))

# 2 — ask the right question
S.append(slide(2,
    kicker("THE KEY INSIGHT") + title("ASK THE RIGHT QUESTION", size=92) +
    mono(110, 250, 830, ['<span style="color:#ff5d8f">✗</span> What color is the pixel at row 8, column 12?'], 28, 90) +
    mono(980, 250, 830, ['<span style="color:#5ee08a">✓</span> Which part of the rocket covers row 8,',
                         '  column 12? nose · body · window · fins · flame'], 28, 120) +
    picture(110, 400, 1270, 464, "parts_vs_colors.png",
            "sprites from color questions (top) vs part questions (bottom)", border=False) +
    text(1430, 430, 380, "Same model.<br>Same pixels.<br>A better question.", 48, TITLE, C["yellow"], 700, 1.15) +
    text(1430, 720, 380, "Parts are meanings — Drex knows a nose cone goes on top and a flame goes below.", 28,
         BODY, C["text"], 400, 1.4) +
    text(110, 880, 1700, "Top: a color per pixel (best of 6 tries). Bottom: a part per pixel — one request per sprite, "
                         "Drex also picks each part's color. Then, at 32×32, every edge pixel asks Drex from its 8 "
                         "neighbours how to smooth itself — local questions, no coordinates.", 28, BODY,
         C["muted"], 400, 1.4)))

# 3 — paint it
S.append(slide(3,
    kicker("PAINT IT") + title("ONE SENTENCE IN, A GIF OUT", size=92) +
    text(110, 240, 1700, "A director LLM (DeepInfra) names the scene, its sprites and their parts. Drex decides every "
                         "pixel of the 32×32 sprites, every part's color, and every frame's position — 512 px GIFs.", 30, BODY, C["muted"], 400,
         1.35) +
    picture(110, 335, 1080, 211, "strip_ufo.png", "ufo abducting a cow, 5 frames", border=False) +
    text(1260, 360, 560, "“a ufo abducting a cow at night”", 30, BODY, C["text"], 600, 1.3) +
    text(1260, 450, 560, "1,046 decisions · 8 Drex calls · 9 s", 26, DOT, C["teal"]) +
    picture(110, 585, 1080, 211, "strip_rocket.png", "rocket launching, 5 frames", border=False) +
    text(1260, 610, 560, "“a rocket launching at night”", 30, BODY, C["text"], 600, 1.3) +
    text(1260, 700, 560, "594 decisions · 5 Drex calls · 5 s", 26, DOT, C["teal"]) +
    text(110, 850, 1700, "Nobody told the rocket to shrink as it flies away. Drex decided that.", 34, DOT, C["yellow"])))

# 4 — Drex Life
S.append(slide(4,
    kicker("LET IT LIVE · DREX LIFE") + title("EVERY PIXEL IS ALIVE", size=92) +
    text(110, 250, 1700, "Describe a world. A director writes its laws of physics in plain English. "
                         "Then every frame, every pixel asks Drex what it becomes.", 36, BODY, C["muted"], 400, 1.35) +
    picture(110, 370, 1700, 270, "strip_fire.png", "forest fire frames", border=False) +
    mono(110, 690, 1060, [
        "This cell is a <span style='color:#5ee08a'>tree</span>. Of its 8 neighbours:",
        "5 tree, 2 <span style='color:#ff5d8f'>fire</span>, 1 ash. Following the rules,",
        "what is this cell in the next step?",
    ], 30) +
    stat(1210, 690, 290, "41,984", "cell decisions") + stat(1520, 690, 290, "1,832", "Drex questions", C["teal"]) +
    text(1210, 870, 600, "“a forest fire: lightning starts fires, fire spreads through trees, burnt ground slowly "
                         "regrows” · 32×32, 40 frames · 22 s · $0.015", 24, BODY, C["muted"], 400, 1.35)))

# 5 — why it works
S.append(slide(5,
    kicker("WHY IT WORKS") + title("THE WORLD LEARNS PHYSICS", size=92) +
    panel(110, 270, 830, 330) +
    text(150, 300, 760, "ONE SITUATION, ONE QUESTION", 38, TITLE, C["teal"], 700) +
    text(150, 360, 760, "Cells in the same situation share one Drex question, and answers are cached across "
                        "steps — 41,984 cell decisions took only 1,832 questions. Drex's answers become the world's physics.", 30, BODY,
         C["text"], 400, 1.45) +
    panel(980, 270, 830, 330) +
    text(1020, 300, 760, "PROBABILITY IS THE DICE", 38, TITLE, C["pink"], 700) +
    text(1020, 360, 760, "The next state is sampled from Drex's calibrated probabilities, so “lightning "
                         "<i>rarely</i> strikes” and “ash <i>slowly</i> regrows” really are rare and slow.", 30, BODY,
         C["text"], 400, 1.45) +
    picture(110, 625, 1700, 270, "strip_zombies.png", "zombie outbreak frames", border=False) +
    text(110, 915, 1700, "“a zombie outbreak in a city” — the infection spreads in glowing waves and the city turns over. "
                         "41,984 cell decisions from 1,350 questions, 26 s, $0.012.", 26, BODY, C["muted"])))

# 6 — real world in
S.append(slide(6,
    kicker("REAL WORLD IN") + title("NEWS & DOCS BECOME WORLDS", size=92) +
    picture(110, 290, 420, 420, "news_bird_flu.png", "bird flu world") +
    text(570, 290, 1240, "THIS WEEK'S NEWS · KEENABLE", 40, TITLE, C["teal"], 700) +
    text(570, 345, 1240, "“bird flu” → 5 UK reports from Nov 10–13, searched and read by Keenable. Every rule cites "
                         "its sources:", 30, BODY, C["text"], 400, 1.4) +
    mono(570, 450, 1240, ["healthy with infected neighbour becomes infected [1, 2, 3]",
                          "healthy with protected neighbour becomes protected [1, 4]"], 28) +
    text(570, 760, 1240, "ANY DOCUMENT · NDI", 40, TITLE, C["yellow"], 700) +
    text(570, 815, 1240, "A scanned PDF → NDI OCR + Extract with page citations → rules that cite their page:",
         30, BODY, C["text"], 400, 1.4) +
    text(570, 870, 1240, "coral with warm neighbour becomes bleached (p. 1) · rock with seaweed neighbour becomes "
                         "seaweed (p. 2)", 26, DOT, C["muted"], 400, 1.4)))

# 7 — god mode
S.append(slide(7,
    kicker("GOD MODE · INTERN") + title("INTERN REWRITES PHYSICS", size=92) +
    text(110, 250, 1700, "Intern runs the world, reads the report, and when a state dies out, the world freezes or one "
                         "state takes over, it edits the English rules and tries again.", 34, BODY, C["muted"], 400,
         1.35) +
    text(110, 365, 300, "BEFORE", 30, DOT, C["pink"]) + text(110, 545, 300, "AFTER", 30, DOT, C["green"]) +
    picture(260, 360, 1550, 443, "god_coral.png", "coral reef before and after Intern", border=False) +
    text(110, 830, 1050, "Two Drexes: one decides every cell of the universe — the other supervises the god.", 38,
         BODY, C["text"], 700, 1.3) +
    stat(1210, 830, 290, "3", "rewrites, 4 runs") + stat(1520, 830, 290, "29", "Drex asks", C["teal"])))

# 8 — built with
rows = [("DREX", "every pixel's part, every cell's state, motion paths — and Intern's System 1", C["yellow"]),
        ("INTERN", "coding agent (built --world / --report) and the god inside the product", C["teal"]),
        ("NDI", "OCR + Extract with page citations: any PDF becomes a world", C["pink"]),
        ("KEENABLE", "this week's news: search + full-article fetch, rules cite sources", C["green"]),
        ("DEEPINFRA", "the directors (scenes + worlds) and Intern's System 2", C["text"]),
        ("ADOBE", "Adobe Fonts and this deck, built in Adobe Express", C["muted"])]
inner = kicker("BUILT WITH") + title("GIFS MADE OF DECISIONS", size=92)
for i, (name, what, col) in enumerate(rows):
    y = 280 + i * 92
    inner += panel(110, y, 1700, 76) + text(150, y + 18, 330, name, 40, TITLE, col, 700, 1.0) + \
        text(500, y + 20, 1280, what, 30, BODY, C["text"])
inner += text(110, 860, 1700, "pixeldrex life “a zombie outbreak” · pixeldrex god “a coral reef” · pixeldrex-web",
              30, DOT, C["teal"]) + text(110, 920, 1700, "github.com/mauryantitans/PixelDrex", 30, DOT, C["yellow"])
S.append(slide(8, inner))

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width={W}">
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="{W}">
<meta name="hz:canvas-height" content="{H}">
<title>PixelDrex — Drexathon pitch</title>
<link rel="stylesheet" href="https://use.typekit.net/hcb0fer.css">
<style>
  html, body {{ margin: 0; padding: 0; background: #05060c; }}
  .slide {{ margin: 0 auto 40px; }}
  .slide b {{ color: {C['yellow']}; font-weight: 700; }}
</style>
</head>
<body>
{chr(10).join(S)}
</body>
</html>
"""
out = HERE / "pixeldrex_deck.html"
out.write_text(html)
print(out, len(html) // 1024, "KB")
