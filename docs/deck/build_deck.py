"""Build docs/deck/pixeldrex_deck.html: an 8-slide 1920x1080 pitch deck with inline PNG assets (for Adobe Express)."""

from deck_kit import BODY, C, DOT, HERE, TITLE, kicker, mono, page, panel, picture, slide, stat, text, title

S = []

# 1 — title
S.append(
    slide(
        1,
        kicker("DREXATHON · WILDCARD TRACK · NOV 14 2026")
        + text(110, 190, 960, "PIXELDREX", 150, TITLE, C["yellow"], 700, 1.0)
        + text(110, 400, 960, "GIFs made entirely of decisions.", 56, BODY, C["text"], 700)
        + text(
            110,
            500,
            860,
            "Drex can't draw. It only answers multiple-choice questions — so every pixel of every "
            "frame is a question, and the answers become animated GIFs.",
            36,
            BODY,
            C["muted"],
            400,
            1.4,
        )
        + text(110, 800, 900, "github.com/mauryantitans/PixelDrex", 32, DOT, C["teal"])
        + picture(
            1170,
            150,
            620,
            620,
            "hero_scene.png",
            "a ghost floating through a haunted house, painted and animated by Drex",
        )
        + text(
            1170,
            800,
            620,
            "“a ghost floating through a haunted house” — painted and animated by Drex: 572 questions, "
            "7 seconds, half a cent.",
            26,
            BODY,
            C["muted"],
            400,
            1.35,
        ),
    )
)

# 2 — ask the right question
S.append(
    slide(
        2,
        kicker("THE KEY INSIGHT")
        + title("ASK THE RIGHT QUESTION", size=92)
        + mono(
            110, 250, 830, ['<span style="color:#ff5d8f">✗</span> What color is the pixel at row 8, column 12?'], 28, 90
        )
        + mono(
            980,
            250,
            830,
            [
                '<span style="color:#5ee08a">✓</span> Which part of the rocket covers row 8,',
                "  column 12? nose · body · window · fins · flame",
            ],
            28,
            120,
        )
        + picture(
            110,
            400,
            1270,
            464,
            "parts_vs_colors.png",
            "sprites from color questions (top) vs part questions (bottom)",
            border=False,
        )
        + text(1430, 430, 380, "Same model.<br>Same pixels.<br>A better question.", 48, TITLE, C["yellow"], 700, 1.15)
        + text(
            1430,
            720,
            380,
            "Parts are meanings — Drex knows a nose cone goes on top and a flame goes below.",
            28,
            BODY,
            C["text"],
            400,
            1.4,
        )
        + text(
            110,
            880,
            1700,
            "Top: a color per pixel (best of 6 tries). Bottom: a part per pixel — one request per sprite, "
            "Drex also picks each part's color. Then, at 32×32, every edge pixel asks Drex from its 8 "
            "neighbours how to smooth itself — local questions, no coordinates.",
            28,
            BODY,
            C["muted"],
            400,
            1.4,
        ),
    )
)

# 3 — paint it
S.append(
    slide(
        3,
        kicker("PAINT IT")
        + title("ONE SENTENCE IN, A GIF OUT", size=92)
        + text(
            110,
            240,
            1700,
            "A director LLM (DeepInfra) names the scene, its sprites and their parts. Drex decides every "
            "pixel of the 32×32 sprites, every part's color, and every frame's position — 512 px GIFs.",
            30,
            BODY,
            C["muted"],
            400,
            1.35,
        )
        + picture(
            110, 335, 1080, 211, "strip_ghost.png", "ghost floating through a haunted house, 5 frames", border=False
        )
        + text(1260, 360, 560, "“a ghost floating through a haunted house”", 30, BODY, C["text"], 600, 1.3)
        + text(1260, 450, 560, "572 Drex questions · 5 calls · 7 s", 26, DOT, C["teal"])
        + picture(110, 585, 1080, 211, "strip_rocket.png", "rocket launching, 5 frames", border=False)
        + text(1260, 610, 560, "“a rocket launching at night”", 30, BODY, C["text"], 600, 1.3)
        + text(1260, 700, 560, "594 decisions · 5 Drex calls · 5 s", 26, DOT, C["teal"])
        + text(
            110,
            850,
            1700,
            "Nobody told the rocket to shrink as it flies away. Drex decided that.",
            34,
            DOT,
            C["yellow"],
        ),
    )
)

# 4 — Drex Life
S.append(
    slide(
        4,
        kicker("THEN WE LET IT LIVE · DREX LIFE")
        + title("EVERY PIXEL IS ALIVE", size=92)
        + text(
            110,
            250,
            1700,
            "Describe a world. A director writes its laws of physics in plain English. "
            "Then every frame, every pixel asks Drex what it becomes.",
            36,
            BODY,
            C["muted"],
            400,
            1.35,
        )
        + picture(110, 370, 1700, 270, "strip_fire.png", "forest fire frames", border=False)
        + mono(
            110,
            690,
            1060,
            [
                "This cell is a <span style='color:#5ee08a'>tree</span>. Of its 8 neighbours:",
                "5 tree, 2 <span style='color:#ff5d8f'>fire</span>, 1 ash. Following the rules,",
                "what is this cell in the next step?",
            ],
            30,
        )
        + stat(1210, 690, 290, "41,984", "cell decisions")
        + stat(1520, 690, 290, "1,832", "Drex questions", C["teal"])
        + text(
            1210,
            870,
            600,
            "“a forest fire: lightning starts fires, fire spreads through trees, burnt ground slowly "
            "regrows” · 32×32, 40 frames · 22 s · $0.015",
            24,
            BODY,
            C["muted"],
            400,
            1.35,
        ),
    )
)

# 5 — why it works
S.append(
    slide(
        5,
        kicker("WHY IT WORKS")
        + title("THE WORLD LEARNS PHYSICS", size=92)
        + panel(110, 270, 830, 330)
        + text(150, 300, 760, "ONE SITUATION, ONE QUESTION", 38, TITLE, C["teal"], 700)
        + text(
            150,
            360,
            760,
            "Cells in the same situation share one Drex question, and answers are cached across "
            "steps — 41,984 cell decisions took only 1,832 questions. Drex's answers become the world's physics.",
            30,
            BODY,
            C["text"],
            400,
            1.45,
        )
        + panel(980, 270, 830, 330)
        + text(1020, 300, 760, "PROBABILITY IS THE DICE", 38, TITLE, C["pink"], 700)
        + text(
            1020,
            360,
            760,
            "The next state is sampled from Drex's calibrated probabilities, so “lightning "
            "<i>rarely</i> strikes” and “ash <i>slowly</i> regrows” really are rare and slow.",
            30,
            BODY,
            C["text"],
            400,
            1.45,
        )
        + picture(110, 625, 1700, 270, "strip_zombies.png", "zombie outbreak frames", border=False)
        + text(
            110,
            915,
            1700,
            "“a zombie outbreak in a city” — the infection spreads in glowing waves and the city turns over. "
            "41,984 cell decisions from 1,350 questions, 26 s, $0.012.",
            26,
            BODY,
            C["muted"],
        ),
    )
)

# 6 — real world in
S.append(
    slide(
        6,
        kicker("REAL WORLD IN")
        + title("NEWS & DOCS BECOME WORLDS", size=92)
        + picture(110, 290, 420, 420, "news_bird_flu.png", "bird flu world")
        + text(570, 290, 1240, "THIS WEEK'S NEWS · KEENABLE", 40, TITLE, C["teal"], 700)
        + text(
            570,
            345,
            1240,
            "“bird flu” → 5 UK reports from Nov 10–13, searched and read by Keenable. Every rule cites its sources:",
            30,
            BODY,
            C["text"],
            400,
            1.4,
        )
        + mono(
            570,
            450,
            1240,
            [
                "healthy with infected neighbour becomes infected [1, 2, 3]",
                "healthy with protected neighbour becomes protected [1, 4]",
            ],
            28,
        )
        + text(570, 760, 1240, "ANY DOCUMENT · NDI", 40, TITLE, C["yellow"], 700)
        + text(
            570,
            815,
            1240,
            "A scanned PDF → NDI OCR + Extract with page citations → rules that cite their page:",
            30,
            BODY,
            C["text"],
            400,
            1.4,
        )
        + text(
            570,
            870,
            1240,
            "coral with warm neighbour becomes bleached (p. 1) · rock with seaweed neighbour becomes seaweed (p. 2)",
            26,
            DOT,
            C["muted"],
            400,
            1.4,
        ),
    )
)

# 7 — god mode
S.append(
    slide(
        7,
        kicker("GOD MODE · INTERN")
        + title("INTERN REWRITES PHYSICS", size=92)
        + text(
            110,
            250,
            1700,
            "Intern runs the world, reads the report, and when a state dies out, the world freezes or one "
            "state takes over, it edits the English rules and tries again.",
            34,
            BODY,
            C["muted"],
            400,
            1.35,
        )
        + text(110, 365, 300, "BEFORE", 30, DOT, C["pink"])
        + text(110, 545, 300, "AFTER", 30, DOT, C["green"])
        + picture(260, 360, 1550, 443, "god_coral.png", "coral reef before and after Intern", border=False)
        + text(
            110,
            830,
            1050,
            "Two Drexes: one decides every cell of the universe — the other supervises the god.",
            38,
            BODY,
            C["text"],
            700,
            1.3,
        )
        + stat(1210, 830, 290, "3", "rewrites, 4 runs")
        + stat(1520, 830, 290, "29", "Drex asks", C["teal"]),
    )
)

# 8 — built with
rows = [
    ("DREX", "every pixel's part, every cell's state, motion paths — and Intern's System 1", C["yellow"]),
    ("INTERN", "coding agent (built --world / --report) and the god inside the product", C["teal"]),
    ("NDI", "OCR + Extract with page citations: any PDF becomes a world", C["pink"]),
    ("KEENABLE", "this week's news: search + full-article fetch, rules cite sources", C["green"]),
    ("DEEPINFRA", "the directors (scenes + worlds) and Intern's System 2", C["text"]),
    ("ADOBE", "Adobe Fonts and this deck, built in Adobe Express", C["muted"]),
]
inner = kicker("BUILT WITH") + title("GIFS MADE OF DECISIONS", size=92)
for i, (name, what, col) in enumerate(rows):
    y = 280 + i * 92
    inner += (
        panel(110, y, 1700, 76)
        + text(150, y + 18, 330, name, 40, TITLE, col, 700, 1.0)
        + text(500, y + 20, 1280, what, 30, BODY, C["text"])
    )
inner += text(
    110,
    860,
    1700,
    "pixeldrex life “a zombie outbreak” · pixeldrex god “a coral reef” · pixeldrex-web",
    30,
    DOT,
    C["teal"],
) + text(110, 920, 1700, "github.com/mauryantitans/PixelDrex", 30, DOT, C["yellow"])
S.append(slide(8, inner))

html = page(S, "PixelDrex — Drexathon pitch")
out = HERE / "pixeldrex_deck.html"
out.write_text(html)
print(out, len(html) // 1024, "KB")
