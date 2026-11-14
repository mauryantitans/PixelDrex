# PixelDrex

> **Every pixel is a decision.** Drex can't draw — it only answers multiple-choice questions. So we made every pixel a question.

Built at **Drexathon** (Nace AI, Nov 14 2026) · Track: 🎨 Wildcard

<p>
<img src="docs/gallery/rocket.gif" width="200">
<img src="docs/gallery/sunrise.gif" width="200">
<img src="docs/gallery/heart.gif" width="200">
<img src="docs/gallery/birds.gif" width="200">
<img src="docs/gallery/ufo.gif" width="200">
</p>

You type an idea. A **director** LLM on DeepInfra turns it into a scene spec (background, up to 3 sprites, how each moves) — it never draws. Then every visual decision is made by [Drex](https://console.nace.ai), Nace's decision model:

1. **Background** — every pixel of a 16×16 grid is one `choice` question over a 14-color palette (256 questions = **one** request), cleaned of stray pixels.
2. **Sprite** — painted in 3 phrasings; extra variations are *sampled from Drex's own per-pixel probabilities* (no extra calls); stray pixels are cleaned; Drex Max looks at all 6 candidates and picks the best. Trimmed and given a 1-px outline.
3. **Motion** — one request per sprite asks "where is it, and how big, in each of 16 frames?" as `score` questions. Scores are **expected values**, so the motion comes out sub-pixel smooth.

≈ 6 Drex calls · ≈ 1,100 decisions · ~5 s · < 1¢ per single-sprite GIF (3 sprites: 16 calls, ~2¢). Nobody told the rocket to shrink as it flies away — Drex decided that.

## Quick start

```bash
python -m venv .venv && .venv/bin/pip install -e .
cp .env.example .env   # add NACE_API_KEY (console.nace.ai) and DEEPINFRA_API_KEY
.venv/bin/pixeldrex "a ufo abducting a cow at night"
```

```text
PixelDrex: a ufo abducting a cow at night
  [  2.6s] director: 'UFO Abducts Cow' with 2 sprite(s): UFO, Cow
  [  3.6s] motion for 'UFO' decided: (15,6) -> (15,6), size 15 -> 15
  [  3.7s] motion for 'Cow' decided: (15,26) -> (15,5), size 13 -> 13
  [  5.9s] background painted (256 pixel decisions)
  [  6.5s] sprite 'UFO' painted 3 ways, judged best of 6
  [  7.1s] sprite 'Cow' painted 3 ways, judged best of 6
  [  7.1s] composited 16 frames

  GIF: out/gallery/20261114-192020-ufo-abducts-cow/anim.gif
  1,890 Drex decisions in 11 calls · 7.1s total · Drex ≈ $0.0131 · director $0.00005
```

Options: `--frames N`, `--ms N`, `--no-outline`, `--spec-only` (show the director's plan), `--spec FILE` (re-paint a saved plan), `--json`.

## Layout

| Path | What |
|---|---|
| `pixeldrex/drex.py` | Async Drex client: typed questions, images, 8-in-flight limit, retries, cost/latency tracking |
| `pixeldrex/pixels.py` | The engine: paint, sample, judge, refine, tiled painting, motion, compositing |
| `pixeldrex/llm.py` | DeepInfra client: chat (director / baseline), vision, FLUX images |
| `pixeldrex/director.py` | Director: idea → scene spec JSON (DeepInfra LLM) |
| `pixeldrex/cli.py` | The `pixeldrex` command; saves GIF, frames, sprites, spec and stats to `out/gallery/` |
| `scripts/scene.py` | Animated scenes (sunrise, rocket, heart, ball) |
| `scripts/drex_gif.py` | v1: every pixel of every frame is a decision (flickery — kept for comparison) |
| `PLAN.md` | Build plan for the hackathon |

Work in progress — more soon.

## License

MIT
