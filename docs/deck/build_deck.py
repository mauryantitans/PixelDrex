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
    text(110, 400, 900, "Every pixel is a decision.", 60, BODY, C["text"], 700) +
    text(110, 500, 860, "Drex can't draw. It only answers multiple-choice questions — so we turned every pixel "
                        "into one. Then we gave the pixels a life.", 36, BODY, C["muted"], 400, 1.4) +
    text(110, 800, 900, "github.com/mauryantitans/PixelDrex", 32, DOT, C["teal"]) +
    picture(1170, 150, 620, 620, "hero_fire.png", "forest fire painted by Drex") +
    text(1170, 800, 620, "A forest fire nobody animated: 17,280 Drex decisions, 15 seconds, $0.004.", 26, BODY,
         C["muted"], 400, 1.35)))

# 2 — a pixel is a question
S.append(slide(2,
    kicker("THE TRICK") + title("A PIXEL IS A QUESTION") +
    picture(110, 300, 600, 600, "pixel_question.png", "rocket sprite on a 32 by 32 grid with one pixel outlined") +
    mono(790, 300, 1020, [
        '<span style="color:#9aa2c2">state</span>  a white rocket with a red nose cone…',
        '<span style="color:#9aa2c2">ask</span>    choice: what color is the pixel at',
        '       row 8, column 16?',
        '<span style="color:#9aa2c2">drex</span>   <span style="color:#ff5d8f">red 0.94</span> · white 0.03 · orange 0.02 …',
    ], 30) +
    text(790, 560, 1020,
         "256 pixels = 256 questions = <b>one</b> request, about a second.<br>"
         "Sprites are painted 3 ways; Drex judges the best of 6.<br>"
         "Motion is <b>score</b> questions — expected values make smooth paths.", 34, BODY, C["text"], 400, 1.5) +
    stat(790, 760, 320, "~1,100", "decisions per GIF") + stat(1140, 760, 320, "~5 s", "start to finish") +
    stat(1490, 760, 320, "&lt; 1¢", "Drex cost", C["teal"])))

# 3 — scenes
scenes = [("scene_ufo.png", "a ufo abducting a cow at night"), ("scene_rocket.png", "a rocket launching at night"),
          ("scene_cat_mouse.png", "a cat chasing a mouse"), ("scene_sunrise.png", "a sunrise over green hills")]
inner = kicker("SCENES") + title("ONE SENTENCE IN, A GIF OUT", size=92)
inner += text(110, 250, 1700, "A director LLM (DeepInfra) plans the scene. Drex paints every pixel and decides how "
                              "everything moves.", 36, BODY, C["muted"])
for i, (f, cap) in enumerate(scenes):
    x = 110 + i * 435
    inner += picture(x, 340, 400, 400, f, cap) + text(x, 770, 400, f"“{cap}”", 28, BODY, C["text"], 600, 1.3)
inner += text(110, 900, 1700, "Nobody told the rocket to shrink as it flies away. Drex decided that.", 34, DOT,
              C["yellow"])
S.append(slide(3, inner))

# 4 — Drex Life
S.append(slide(4,
    kicker("DREX LIFE") + title("EVERY PIXEL IS ALIVE") +
    text(110, 250, 1700, "Describe a world. A director writes its laws of physics in plain English. "
                         "Then every step, every cell asks Drex what it becomes.", 36, BODY, C["muted"], 400, 1.35) +
    picture(110, 370, 1700, 274, "strip_fire.png", "forest fire frames", border=False) +
    mono(110, 690, 1060, [
        "This cell is a <span style='color:#5ee08a'>tree</span>. Of its 8 neighbours:",
        "5 tree, 2 <span style='color:#ff5d8f'>fire</span>, 1 ash. Following the rules,",
        "what is this cell in the next step?",
    ], 30) +
    stat(1210, 690, 290, "17,280", "cell decisions") + stat(1520, 690, 290, "191", "Drex questions", C["teal"]) +
    text(1210, 870, 600, "“a forest fire: lightning starts fires, fire spreads through trees, burnt ground slowly "
                         "regrows” · 15 s · $0.004", 24, BODY, C["muted"], 400, 1.35)))

# 5 — why it works
S.append(slide(5,
    kicker("WHY IT WORKS") + title("THE WORLD LEARNS PHYSICS", size=92) +
    panel(110, 270, 830, 330) +
    text(150, 300, 760, "ONE SITUATION, ONE QUESTION", 38, TITLE, C["teal"], 700) +
    text(150, 360, 760, "Cells in the same situation share one Drex question, and answers are cached across "
                        "steps. By the end of the forest fire, each step needed about one new question.", 30, BODY,
         C["text"], 400, 1.45) +
    panel(980, 270, 830, 330) +
    text(1020, 300, 760, "PROBABILITY IS THE DICE", 38, TITLE, C["pink"], 700) +
    text(1020, 360, 760, "The next state is sampled from Drex's calibrated probabilities, so “lightning "
                         "<i>rarely</i> strikes” and “ash <i>slowly</i> regrows” really are rare and slow.", 30, BODY,
         C["text"], 400, 1.45) +
    picture(110, 625, 1700, 274, "strip_zombies.png", "zombie outbreak frames", border=False) +
    text(110, 915, 1700, "“a zombie outbreak in a city” — the city grows, zombies creep in from the corners and take "
                         "it. 40,960 cell decisions from 590 questions, 17 s, $0.008.", 26, BODY, C["muted"])))

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
rows = [("DREX", "every pixel, every cell, sprite judging, motion paths — and Intern's System 1", C["yellow"]),
        ("INTERN", "coding agent (built --world / --report) and the god inside the product", C["teal"]),
        ("NDI", "OCR + Extract with page citations: any PDF becomes a world", C["pink"]),
        ("KEENABLE", "this week's news: search + full-article fetch, rules cite sources", C["green"]),
        ("DEEPINFRA", "the directors (scenes + worlds) and Intern's System 2", C["text"]),
        ("ADOBE", "Adobe Fonts and this deck, built in Adobe Express", C["muted"])]
inner = kicker("BUILT WITH") + title("EVERY PIXEL WAS A DECISION", size=92)
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
