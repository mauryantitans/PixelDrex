# PixelDrex

> **Every pixel is a decision.** Drex can't draw — it only answers multiple-choice questions. So we made every pixel a question.

Built at **Drexathon** (Nace AI, Nov 14 2026) · Track: 🎨 Wildcard

Two things you can do with it:

- **🧬 Drex Life** — every pixel is a living agent. You describe a world; the laws of physics are written in plain English; every step, every cell asks Drex what it becomes next.
- **🎬 Scenes** — type an idea; Drex paints every pixel of the background and sprites and decides how everything moves.

## 🧬 Drex Life

<p>
<img src="docs/gallery/life_forest_fire.gif" width="240" alt="forest fire">
<img src="docs/gallery/life_zombies.gif" width="240" alt="zombie outbreak">
</p>

*Left: "a forest fire: lightning starts fires, fire spreads through trees, burnt ground slowly regrows" — lightning strikes, a burning front spreads as a ring, ash follows, trees regrow in the burn scar, and a second strike starts the next wave. Right: "a zombie outbreak in a city" — a human city grows, zombies creep in from the corners and take it.* Nobody animated either one.

```bash
.venv/bin/pixeldrex life "a zombie outbreak in a city"
```

1. A **director** LLM (DeepInfra) designs the world: 3–5 cell states with colors, 3–6 rules in plain English, and a starting layout. It never decides a single cell.
2. **Drex seeds the world**: one `choice` question per cell (32×32 = 1,024 questions).
3. **Every step, every cell asks Drex**: *"This cell is currently a tree. Of its 8 neighbours: 5 tree, 2 fire, 1 ash. Following the rules, what is this cell in the next step?"*
   - **Cells in the same situation share one question**, and Drex's answers are **cached across steps** — the world learns its physics from Drex as it goes. The forest fire made **17,280 cell decisions from 191 unique questions** (15 s, $0.004); by the end, each step needed about one new question.
   - The next state is **sampled from Drex's calibrated probabilities**, so "lightning *rarely* strikes" and "ash *slowly* regrows" really are rare and slow. Randomness in the world *is* Drex's uncertainty.
   - If the rules mention directions (sand *falls*, wind blows *east*), cells see which neighbour is where; otherwise only neighbour counts matter, which collapses far more cells into one question.

| World | Grid × steps | Cell decisions | Unique Drex questions | Time | Drex cost |
|---|---|---|---|---|---|
| Forest fire | 24×24 × 30 | 17,280 | 191 | 15 s | $0.004 |
| Zombie outbreak | 32×32 × 40 | 40,960 | 590 | 17 s | $0.008 |

### 😇 God mode: Intern rewrites the laws of physics

```bash
.venv/bin/pixeldrex god "a coral reef: coral grows, warm water bleaches coral, fish help bleached coral recover"
```

[Intern](https://github.com/nace-ai/intern), Nace's coding agent, becomes the god of a Drex Life world. It runs the world
(`pixeldrex life --world worlds/<name>.json --report`), reads the report, and if a state died out, the world froze,
or one state took over, it **edits the English rules in the world file** and runs it again — up to 4 times.
Two Drexes are at work: one decides every cell of the universe; the other, as Intern's System 1, supervises the god.

<img src="docs/gallery/god_coral_before_after.png" width="720" alt="coral reef before and after Intern">

*Top: the director's original rules — a coral blob drips down and the world dies. Bottom: after Intern's 3 rewrites
(fish that can come back on their own, density-based neighbour counts, overcrowding that causes bleaching) — a living
reef where coral spreads, bleaches and recovers, and a school of fish moves through. 4 world runs, 12 Intern turns,
128 s, 29 System 1 (Drex) asks; the full agent log is in `intern_logs/`.*

### 📄 Any document becomes a world (NDI)

```bash
.venv/bin/pixeldrex life --doc docs/samples/coral_reef_field_notes.pdf --save-world worlds/reef.json
.venv/bin/pixeldrex god --world worlds/reef.json      # optional: let Intern fix the physics
```

[NDI](https://console.nace.ai) (Nace Document Intelligence) reads a PDF — a public URL or a local file it uploads, scanned
pages included (OCR) — and **Extract** fills a schema with the document's *actors* and *interactions* (what spreads to,
turns into, kills or helps what, and how fast), each **with citations to the page it came from**. The director turns
those facts into states and rules, and **every rule ends with its source page**:

```text
coral with warm neighbour becomes bleached (p. 1)
rock with coral neighbour becomes coral (p. 1)
rock with seaweed neighbour becomes seaweed (p. 2)
```

In god mode, Intern keeps the document's rules and citations, and tags every law it invents with `(god)` — so each
law of the final world says whether it came from the document or from the god. The sample is a 2-page,
scanned-style field report (`scripts/make_sample_doc.py`); NDI read it in ~18 s and put each fact on the right page.

<img src="docs/gallery/doc_reef_before_after.png" width="720" alt="reef built from the field notes, before and after Intern">

*Top: the world built straight from the field notes froze (a heat patch flickers; the rules were written from the wrong cell's point of view). Bottom: after Intern's rewrites (it also deleted a rule about parrotfish, a state that did not exist) coral recolonises the rock and seaweed takes over the heat-damaged patch — the "phase shift" the notes describe. Intern reported honestly that it narrowly missed its own activity target (185 of 192 changed cells).*


### 📰 This week's news becomes a world (Keenable)

```bash
.venv/bin/pixeldrex life --news "bird flu"
```

[Keenable](https://keenable.ai) searches the last 7 days of news on the topic and reads the top articles in full (its
keyless public endpoints; set `KEENABLE_API_KEY` to use a key). The director turns the reporting into states and rules,
and **every rule cites the articles it came from**. In the web app, tick *"Build the world from this week's news"* in
Drex Life mode and the linked headlines appear under the rules.

<p>
<img src="docs/gallery/news_bird_flu.gif" width="240" alt="bird flu world from this week's news">
<img src="docs/gallery/news_wildfire.gif" width="240" alt="wildfire world from this week's news">
</p>

*Left, "bird flu" on Nov 14 2026: five UK reports (outbreaks near Dereham and Dersingham, a national housing order)
→ `healthy with infected neighbour becomes infected [1, 2, 3]`, `infected becomes culled [2, 3]`,
`healthy with protected neighbour becomes protected [1, 4]` → rings of infection and culling while the protected zone
spreads. Right, "wildfire": reporting on New Hampshire's Wild River Fire → `forest with a fire neighbour often becomes
fire [2, 3]`, `fire with a rain neighbour rarely becomes ash [1, 4]`.*

## 🎬 Scenes

<p>
<img src="docs/gallery/ufo.gif" width="200">
<img src="docs/gallery/rocket.gif" width="200">
<img src="docs/gallery/sunrise.gif" width="200">
<img src="docs/gallery/heart.gif" width="200">
<img src="docs/gallery/birds.gif" width="200">
</p>

You type an idea. The director turns it into a scene spec (background, up to 3 sprites, how each moves). Then every visual decision is made by [Drex](https://console.nace.ai), Nace's decision model:

1. **Background** — every pixel of a 16×16 grid is one `choice` question over a 15-color palette, plus 16 "which color covers most of row r?" questions, all in **one** request. Each pixel takes the argmax of P(pixel) × P(row)^0.5, so calibrated row answers fill in areas the pixel answers are unsure about.
2. **Sprite** — painted in 3 phrasings; extra variations are *sampled from Drex's own per-pixel probabilities* (no extra calls); stray pixels are cleaned; Drex Max looks at all 6 candidates and picks the best. Trimmed and given a 1-px outline.
3. **Motion** — one request per sprite asks "where is it, and how big, in each of 16 frames?" as `score` questions. Scores are **expected values**, so the motion comes out sub-pixel smooth.

≈ 6 Drex calls · ≈ 1,100 decisions · ~5 s · < 1¢ per single-sprite GIF. Nobody told the rocket to shrink as it flies away — Drex decided that.

```text
$ pixeldrex "a ufo abducting a cow at night"
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

## Quick start

```bash
python -m venv .venv && .venv/bin/pip install -e .
cp .env.example .env   # add NACE_API_KEY (console.nace.ai) and DEEPINFRA_API_KEY
.venv/bin/pixeldrex life "a forest fire"        # Drex Life
.venv/bin/pixeldrex "a rocket launching at night" # a scene
.venv/bin/pixeldrex-web                         # web app on http://127.0.0.1:8000
```

The web app has both modes. In **Drex Life** you watch the world evolve frame by frame as Drex decides it, with live population bars for each state, the rules, and counters for cell decisions vs unique Drex questions. In **Scene** you see the director's plan, each layer as it's painted, the motion paths Drex chose, and live decision/cost counters. Everything lands in the gallery.

## Layout

| Path | What |
|---|---|
| `pixeldrex/drex.py` | Async Drex client: typed questions, images, 8-in-flight limit, retries, cost/latency tracking |
| `pixeldrex/life.py` | Drex Life: world design, seeding, per-situation questions with caching, probabilistic steps |
| `pixeldrex/god.py` | God mode: Intern tunes a world's rules until it stays alive |
| `pixeldrex/ndi.py` | NDI: upload or link a document, Extract actors and interactions with page citations, build a cited world |
| `docs/samples/` | A 2-page scanned-style field report for the NDI demo |
| `pixeldrex/news.py` | Keenable: search this week's news and read the top articles; build a world whose rules cite them |
| `scripts/intern.sh`, `intern_logs/` | Run Intern headless on this repo; every Intern run's JSON events and reply |
| `worlds/` | Saved worlds (rules in English) |
| `pixeldrex/pixels.py` | Scene engine: paint, background fusion, sample, judge, refine, tiled painting, motion, compositing |
| `pixeldrex/director.py` | Scene director: idea → scene spec JSON (DeepInfra LLM) |
| `pixeldrex/llm.py` | DeepInfra client: chat, vision, FLUX images |
| `pixeldrex/cli.py` | The `pixeldrex` and `pixeldrex life` commands; saves GIFs, frames, specs and stats to `out/gallery/` |
| `pixeldrex/web.py`, `pixeldrex/web/index.html` | The web app (FastAPI + server-sent events) |
| `scripts/` | Experiments: scenes, v1 per-frame painting, large images, background fusion, Life demos |
| `bench/` | Side experiment: Drex vs LLMs writing pixel grids as text |
| `PLAN.md` | Build plan for the hackathon |

## License

MIT
