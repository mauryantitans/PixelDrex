# Drexathon submission — PixelDrex

**Title:** PixelDrex — every pixel is a decision

**Track:** 🎨 Wildcard

**Repo:** https://github.com/mauryantitans/PixelDrex

**Presentation:** Adobe Express deck (8 slides) — link from the Express share menu

**Demo:** `pixeldrex-web` (live) · animated results in the README gallery

---

## One-liner

Drex can't draw — it only answers multiple-choice questions — so we turned every pixel into a question, then gave the pixels a life: worlds whose laws of physics are plain English, where Drex decides what every cell becomes, every step.

## Short explanation (~100 words)

PixelDrex makes Drex paint and animate pixel art, one decision per pixel. In **Drex Life**, every pixel is a living agent: you describe a world, a director writes its rules in English, and every step each cell asks Drex "I'm a tree with 2 burning neighbours — what am I next?" Cells in the same situation share one question and answers are cached, so a forest fire took 17,280 cell decisions from just 191 Drex questions (15 s, $0.004). Worlds can come from this week's news (Keenable) or any PDF (NDI), with every rule citing its source — and in **god mode**, Intern rewrites a dying world's laws of physics until it comes alive.

## Full explanation (~300 words)

Drex can't draw. It only answers typed multiple-choice questions with calibrated probabilities. PixelDrex takes that literally:

**Every pixel is a question.** A 16×16 sprite is 256 `choice` questions in one Drex request. Sprites are painted three ways and Drex Max judges the best of six; motion comes from `score` questions whose expected values give smooth paths. Type "a ufo abducting a cow" and a director LLM plans the scene while Drex paints and animates it: ~1,100 decisions, ~5 s, under a cent. Nobody told the rocket to shrink as it flies away — Drex decided that.

**Every pixel is alive (Drex Life).** Describe a world; a director writes its laws of physics in plain English; then every step, every cell asks Drex what it becomes given its 8 neighbours. Two ideas make it work: cells in the same situation share one question and answers are cached (the world *learns its physics* — a 24×24 forest fire made 17,280 decisions from 191 questions), and the next state is *sampled from Drex's calibrated probabilities*, so "lightning rarely strikes" and "ash slowly regrows" really are rare and slow. Forest fires spread as burning rings and regrow; a zombie outbreak overruns a city.

**The real world in.** `--news "bird flu"` uses Keenable to search and read this week's reporting and builds a world whose rules cite the articles ([1, 2, 3]). `--doc file.pdf` uses NDI to OCR and extract a document's actors and interactions with page citations, so every rule cites its page (p. 2).

**God mode.** Intern becomes the god of a world: it runs it, reads the report, and when a state dies out or the world freezes, rewrites the English rules and tries again — keeping document citations and tagging its own laws (god). A dead coral reef became a living one after 3 rewrites. Two Drexes: one decides every cell of the universe, the other (Intern's System 1) supervises the god.

## How we used each tool

- **Drex (Max v1.1):** every pixel, every cell decision, sprite judging, motion paths — and Intern's System 1.
- **Intern:** our coding agent for part of the build (it implemented `--world` / `--report`; logs in `intern_logs/`), and inside the product as the god that rewrites a world's rules.
- **NDI:** upload + OCR + Extract with page citations — any PDF becomes a world with cited rules.
- **Keenable:** search (last 7 days) + full-article fetch — this week's news becomes a world with cited rules.
- **DeepInfra:** the scene and world directors, and Intern's System 2 (DeepSeek-V4-Pro).
- **Adobe:** Adobe Fonts and the pitch deck, built in Adobe Express.

## Numbers (real runs, Nov 14 2026)

| Run | Decisions | Drex questions / calls | Time | Drex cost |
|---|---|---|---|---|
| Forest fire (Life, 24×24 × 30) | 17,280 cells | 191 questions | 15 s | $0.004 |
| Zombie outbreak (Life, 32×32 × 40) | 40,960 cells | 590 questions | 17 s | $0.008 |
| "a ufo abducting a cow" (scene) | 1,890 | 11 calls | 7 s | $0.013 |
| God mode, coral reef | 4 world runs, 3 rewrites | 29 Intern System 1 asks | 128 s | — |

## Honest limits

- Drex paints small, iconic subjects well; large detailed images pixel-by-pixel don't work (we tried — plain downscaling beat it; see `scripts/` and the gallery).
- Not every world is interesting on the first try (rock-paper-scissors was noise; a world built straight from the sample PDF froze) — which is exactly what god mode is for, though it doesn't always hit its target (it reported missing one by 7 cells).
