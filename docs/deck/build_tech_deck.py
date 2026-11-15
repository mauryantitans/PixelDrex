"""Build docs/deck/pixeldrex_tech_deck.html: a 6-slide, 2-minute technical deck (for Adobe Express)."""

from deck_kit import BODY, DOT, HERE, TITLE, C, kicker, mono, page, panel, picture, slide, text, title

N = 6


def flow_box(x, y, w, h, head, body, color=None):
    return (
        panel(x, y, w, h)
        + text(x + 24, y + 22, w - 48, head, 30, DOT, color or C["yellow"], 400, 1.2)
        + text(x + 24, y + 72, w - 48, body, 24, BODY, C["muted"], 400, 1.35)
    )


def arrow(x, y, glyph="→"):
    return text(x, y, 50, glyph, 44, DOT, C["teal"], extra="text-align:center;")


def column(x, y, w, h, head, body):
    return (
        panel(x, y, w, h)
        + text(x + 32, y + 28, w - 64, head, 34, DOT, C["yellow"], 400, 1.2)
        + text(x + 32, y + 92, w - 64, body, 27, BODY, C["text"], 400, 1.4)
    )


S = []

# 1 — title
S.append(
    slide(
        1,
        kicker("PIXELDREX · TECHNICAL DEEP DIVE")
        + text(110, 170, 1000, "UNDER<br>THE HOOD", 130, TITLE, C["yellow"], 700, 1.0)
        + text(
            110, 460, 960, "How a decision model paints, animates and evolves pixels.", 48, BODY, C["text"], 700, 1.2
        )
        + text(
            110,
            600,
            900,
            "Drex never sees a canvas. It answers typed multiple-choice questions with calibrated "
            "probabilities. Every pixel, color, position and pose in a PixelDrex GIF is the answer to one of them.",
            34,
            BODY,
            C["muted"],
            400,
            1.4,
        )
        + text(110, 880, 900, "github.com/mauryantitans/PixelDrex", 32, DOT, C["teal"])
        + picture(1170, 150, 620, 620, "tech_hero.png", "a ghost floating through a haunted house")
        + text(
            1170,
            800,
            620,
            "“a ghost floating through a haunted house”<br>572 Drex questions · 5 calls · 5.5 s · half a cent",
            26,
            BODY,
            C["muted"],
            400,
            1.4,
        ),
        N,
    )
)

# 2 — the primitive
S.append(
    slide(
        2,
        kicker("THE PRIMITIVE")
        + title("ONE PIXEL, ONE QUESTION", size=92)
        + mono(
            110,
            250,
            960,
            [
                '<span style="color:#9aa2c2">"p_08_12": {</span>',
                '  <span style="color:#4fd1c5">"type"</span>: "choice",',
                '  <span style="color:#4fd1c5">"question"</span>: "Which part of the ghost',
                '    covers row 8, column 12?",',
                '  <span style="color:#4fd1c5">"criteria"</span>: sheet · left eye ·',
                "    right eye · mouth · empty",
                '<span style="color:#9aa2c2">}</span>',
            ],
            26,
        )
        + text(
            1130,
            255,
            690,
            "• <b>16×16 sprite = 256 questions = 1 request</b> (up to 512 per request, 8 in flight)<br>"
            "• Symmetric sprites ask the left half and mirror it<br>"
            "• Each part's color is one more question in the same request<br>"
            "• <b>Parts, not colors:</b> parts carry meaning, so Drex knows a nose cone goes on top",
            28,
            BODY,
            C["text"],
            400,
            1.5,
        )
        + picture(110, 630, 960, 351, "parts_vs_colors.png", "color-per-pixel vs part-per-pixel sprites", border=False)
        + text(
            1130,
            680,
            690,
            "Top: a color per pixel, best of 6 tries.<br>Bottom: a part per pixel, one call per sprite.",
            28,
            BODY,
            C["muted"],
            400,
            1.45,
        )
        + text(1130, 830, 690, "Same model. A better question.", 40, TITLE, C["yellow"], 700, 1.15),
        N,
    )
)

# 3 — resolution without coordinates
S.append(
    slide(
        3,
        kicker("16 → 32 → 64 → 128")
        + title("RESOLUTION WITHOUT COORDINATES", size=84)
        + text(
            110,
            240,
            960,
            "Drex is strong at local judgments and weak at exact positions, so we never ask about row 27 of 32.",
            30,
            BODY,
            C["muted"],
            400,
            1.4,
        )
        + text(110, 350, 960, "<b>1.</b> Paint the clean 16×16 part layout in one request.", 30, BODY, C["text"], 400)
        + text(
            110,
            410,
            960,
            "<b>2.</b> Double it. Every edge pixel asks Drex, from its 8 neighbours only:",
            30,
            BODY,
            C["text"],
            400,
            1.35,
        )
        + mono(
            110,
            500,
            960,
            [
                "I'm 'sheet'. North: sheet · East: empty ·",
                "South: mouth · West: sheet … Which should I",
                "be so the outline is smooth?",
            ],
            28,
        )
        + text(
            110,
            760,
            960,
            "<b>3.</b> Identical neighbourhoods share one question: about <b>1 Drex call per doubling</b>, "
            "and the same trick smooths backgrounds.",
            30,
            BODY,
            C["text"],
            400,
            1.4,
        )
        + picture(1150, 230, 670, 689, "resolution_ladder.png", "the same sprites at 16, 32, 64 and 128 pixels"),
        N,
    )
)

# 4 — motion and change
S.append(
    slide(
        4,
        kicker("ANIMATION")
        + title("MOTION AND CHANGE ARE DECISIONS TOO", size=78)
        + mono(
            110,
            240,
            1700,
            [
                "For each of 16 frames, in one request per sprite:",
                '<span style="color:#4fd1c5">score</span>  x · y · size · tilt (leaning left … right) · '
                "shape (stretched … squashed)",
                '<span style="color:#4fd1c5">choice</span> "Which pose is the tree in during frame 7?"  '
                "sapling · young tree · full tree",
            ],
            28,
        )
        + text(110, 540, 840, "Poses: 3 shapes, Drex picks one per frame", 28, DOT, C["yellow"])
        + picture(110, 590, 840, 160, "strip_sapling.png", "a sapling growing into a tree", border=False)
        + text(980, 540, 840, "Squash and stretch, decided by Drex", 28, DOT, C["yellow"])
        + picture(980, 590, 840, 160, "strip_ball.png", "a ball bouncing and squashing", border=False)
        + text(
            110,
            800,
            1700,
            "A <b>score</b> question returns an expected value, so paths come out sub-pixel smooth: no keyframes, "
            "no physics code. Shape-changing sprites get 2–4 poses painted with shared colors in one shared "
            "frame, so nothing jumps.",
            30,
            BODY,
            C["text"],
            400,
            1.4,
        ),
        N,
    )
)

# 5 — Drex Life
S.append(
    slide(
        5,
        kicker("THE EXTENSION · DREX LIFE")
        + title("THE WORLD LEARNS ITS PHYSICS", size=88)
        + picture(125, 240, 1670, 270, "strip_fire.png", "forest fire frames", border=False)
        + column(
            110,
            560,
            540,
            400,
            "SHARED QUESTIONS",
            "A cell asks with its state and neighbour counts: “I'm a tree with 2 burning neighbours. "
            "What am I next?” Cells in the same situation share it.",
        )
        + column(
            690,
            560,
            540,
            400,
            "CACHED ACROSS FRAMES",
            "Situations repeat, so answers are reused. A 32×32 × 40-frame fire: "
            "<b>41,984 cell decisions from 1,832 questions</b>, 22 s, under 2¢.",
        )
        + column(
            1270,
            560,
            540,
            400,
            "SAMPLED, NOT ARGMAX",
            "The next state is sampled from Drex's calibrated probabilities (T = 0.8), so "
            "“lightning rarely strikes” really is rare.",
        ),
        N,
    )
)

# 6 — architecture
S.append(
    slide(
        6,
        kicker("ARCHITECTURE")
        + title("THE PIPELINE", size=92)
        + flow_box(110, 250, 300, 230, "IDEA", "one sentence, typed in the web app or CLI")
        + arrow(410, 335)
        + flow_box(460, 250, 300, 230, "DIRECTOR", "DeepSeek-V4 on DeepInfra writes the scene spec as JSON")
        + arrow(760, 335)
        + flow_box(810, 250, 300, 230, "DREX", "background ∥ sprites + poses ∥ motion, all in parallel")
        + arrow(1110, 335)
        + flow_box(1160, 250, 300, 230, "COMPOSE", "shading, outline, tilt, squash")
        + arrow(1460, 335)
        + flow_box(1510, 250, 300, 230, "512 px GIF", "streamed live to the browser", C["green"])
        + flow_box(110, 540, 300, 230, "KEENABLE", "this week's news → a world whose rules cite articles", C["teal"])
        + flow_box(460, 540, 300, 230, "NDI", "any PDF → a world whose rules cite pages", C["teal"])
        + arrow(760, 625)
        + flow_box(810, 540, 300, 230, "DREX LIFE", "every pixel asks what it becomes next")
        + arrow(1110, 625, "⇄")
        + flow_box(
            1160,
            540,
            650,
            230,
            "INTERN · GOD MODE",
            "runs the world, reads the report, rewrites the English rules until it lives. Drex is Intern's System 1.",
            C["pink"],
        )
        + text(
            110,
            820,
            1700,
            "<b>5–9 Drex calls · 5–10 s · about 1¢ per GIF</b>",
            34,
            BODY,
            C["text"],
            400,
        )
        + text(
            110,
            880,
            1700,
            "Async Drex client (8 in flight, retries, cost tracking) · FastAPI + server-sent events · "
            "20 offline tests and lint in CI",
            28,
            BODY,
            C["muted"],
            400,
            1.4,
        ),
        N,
    )
)

out = HERE / "pixeldrex_tech_deck.html"
out.write_text(page(S, "PixelDrex — technical deep dive"))
print(out, out.stat().st_size // 1024, "KB")
