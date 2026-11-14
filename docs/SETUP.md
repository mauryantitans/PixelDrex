# Setup

Everything you need to run PixelDrex from a fresh machine: the command line, the web app, Drex Life, news and
document worlds, and god mode. Commands are for macOS / Linux; Windows notes are at the end.

## 1. Prerequisites

| What | Needed for | Check |
|---|---|---|
| **Python 3.10+** (tested on 3.13) | everything | `python3 --version` |
| **git** | getting the code | `git --version` |
| **A Nace console API key** (`nace_sk_…`) | Drex and NDI — every pixel decision | [console.nace.ai](https://console.nace.ai) |
| **A DeepInfra API key** (`sk-di-…`) | the directors (scene and world planning) and Intern's System 2 | [deepinfra.com](https://deepinfra.com) |
| *Optional:* **uv** + **Python 3.12+** | god mode (Intern) | `uv --version` |
| *Optional:* **Node.js + Playwright, ffmpeg** | re-recording the demo video only | `node --version`, `ffmpeg -version` |
| *Optional:* a Keenable key | not needed — news mode uses Keenable's keyless public endpoint | — |

### Get the keys

1. **Nace (Drex + NDI):** sign in at [console.nace.ai](https://console.nace.ai) (Google or GitHub). At Drexathon, go to
   **Billing** and redeem the event code for credits. Then **API Keys → Create key** and copy it (it is shown once).
2. **DeepInfra:** at Drexathon the organizers hand out a team key; otherwise create one at deepinfra.com.

## 2. Install

```bash
git clone https://github.com/mauryantitans/PixelDrex.git
cd PixelDrex
python3 -m venv .venv
.venv/bin/pip install -e .
```

This installs two commands into `.venv/bin/`: `pixeldrex` (command line) and `pixeldrex-web` (web app).

## 3. Add your keys

```bash
cp .env.example .env
```

Open `.env` and fill in:

```ini
NACE_API_KEY=nace_sk_...
DEEPINFRA_API_KEY=sk-di-...
```

`.env` is git-ignored — never commit it. Every PixelDrex module reads it from the repo root, so run commands from the
repo folder.

## 4. Check it works

```bash
.venv/bin/pixeldrex "a rocket launching at night" --spec-only     # DeepInfra only: prints the director's plan
.venv/bin/pixeldrex "a rocket launching at night"                 # Drex paints and animates it (~5-10 s)
```

The second command ends with a line like:

```text
  GIF: out/gallery/20261114-210000-night-rocket-launch/anim.gif
  594 Drex decisions in 5 calls · 4.8s total · Drex ≈ $0.0047
```

Open that `anim.gif`. If you see a rocket, everything is wired up.

## 5. Use it

### Scenes (the main idea)

```bash
.venv/bin/pixeldrex "a ufo abducting a cow at night"
.venv/bin/pixeldrex "a hot air balloon rising over green hills" --frames 20
.venv/bin/pixeldrex --spec out/gallery/<run>/spec.json     # re-paint a saved plan without the director
```

Options: `--frames N` (default 16), `--ms N` per frame (90), `--no-outline`, `--spec-only`, `--spec FILE`, `--json`.
Front-facing subjects work best (rockets, UFOs, balloons, ghosts, jellyfish); side-view animals come out blobby.

### Drex Life (the extension)

```bash
.venv/bin/pixeldrex life "a zombie outbreak in a city"                 # a fresh world
.venv/bin/pixeldrex life --world worlds/forest-fire-cycle.json         # replay known-good rules
.venv/bin/pixeldrex life --news "wildfire"                             # a world from this week's news (Keenable)
.venv/bin/pixeldrex life --doc docs/samples/coral_reef_field_notes.pdf --save-world worlds/reef.json   # from a PDF (NDI)
.venv/bin/pixeldrex life --world worlds/zombie-outbreak-city.json --report   # quiet run, prints a JSON report
```

Options: `--size N` (grid, default 32), `--steps N` (default 40), `--temp T` (sampling temperature, default 0.8),
`--save-world PATH`. Fresh worlds vary run to run; the files in `worlds/` replay the best ones.

### Web app

```bash
.venv/bin/pixeldrex-web          # http://127.0.0.1:8000
```

- **Scene** tab (default): type an idea or click an example; watch the plan, each painted layer, the motion paths and
  live decision / cost counters.
- **Drex Life** tab: describe a world, tick *"Build the world from this week's news"*, or click a **saved world** to
  replay it; frames stream in live with population bars and the rules.
- Every result is added to the gallery at the bottom (files in `out/gallery/`).
- Different port: `PORT=8001 .venv/bin/pixeldrex-web`.

### God mode (Intern rewrites a world's rules)

Needs [Intern](https://github.com/nace-ai/intern), Nace's coding agent (Python 3.12+):

```bash
uv tool install "intern-agent @ git+https://github.com/nace-ai/intern"
intern --version
```

```bash
.venv/bin/pixeldrex god "a coral reef: coral grows, warm water bleaches coral, fish help bleached coral recover"
.venv/bin/pixeldrex god --world worlds/reef-from-field-notes.json
```

Intern uses `DEEPINFRA_API_KEY` (System 2, default `deepinfra/deepseek-ai/DeepSeek-V4-Pro`) and `NACE_API_KEY`
(System 1, Drex). A run takes ~2 minutes (up to 4 world runs); its full log goes to `intern_logs/`.
`scripts/intern.sh "task"` runs Intern headless on this repo as a coding agent, with the same keys and logging.

## 6. Configuration

All optional; put them in `.env` or export them.

| Variable | Default | What |
|---|---|---|
| `NACE_API_KEY` | — (required) | Drex + NDI key |
| `DEEPINFRA_API_KEY` | — (required) | directors + Intern System 2 |
| `NACE_BASE_URL` | `https://console.nace.ai` | Nace API base URL |
| `DREX_MODEL` | `drex-max-v1.1` | Drex model for every decision |
| `DREX_MAX_IN_FLIGHT` | `8` | concurrent Drex requests (free tier allows 8, paid 16) |
| `DREX_PRICE_PER_M` | `0.06` | $ per million input tokens, only for the cost display |
| `DI_TEXT_MODEL` | `deepseek-ai/DeepSeek-V4-Flash` | director LLM on DeepInfra |
| `KEENABLE_API_KEY` | unset | use a Keenable key instead of the public endpoint |
| `INTERN_SYSTEM2` / `INTERN_SYSTEM1` | `deepinfra/deepseek-ai/DeepSeek-V4-Pro` / `drex-max-v1.1` | god mode's models |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | web app address |

## 7. Where things go

```text
out/gallery/<time>-<title>/        one folder per run (git-ignored)
  anim.gif                         the GIF
  spec.json / world.json           the director's scene plan / the world's rules
  stats.json                       decisions, calls, time, cost, motion tracks or Life report
  sheet.png, sprite*.png, background.png        (scenes) frames and layers
  news.json / document.json                     (Life) the cited sources
worlds/*.json                      saved worlds you can replay (committed)
intern_logs/                       every Intern run: JSON events + final reply
```

## 8. Rebuilding the deck and video (optional)

```bash
.venv/bin/python docs/deck/build_assets.py && .venv/bin/python docs/deck/build_deck.py   # -> docs/deck/pixeldrex_deck.html
```

The deck HTML was imported into Adobe Express with the Adobe connector. To re-record the demo video, start
`pixeldrex-web`, record each run with Playwright, then stitch them:

```bash
node scripts/record_demo.js out/videos demo_scene_rocket scene "a rocket launching at night"
node scripts/record_demo.js out/videos demo_life_forest_fire replay forest-fire-cycle
node scripts/record_demo.js out/videos demo_life_news_wildfire news "wildfire"
for f in out/videos/*.webm; do ffmpeg -y -i "$f" -c:v libx264 -pix_fmt yuv420p "${f%.webm}.mp4"; done
.venv/bin/python scripts/make_demo_video.py out/videos docs/video/pixeldrex_demo.mp4
```

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| `NACE_API_KEY is not set` / `DEEPINFRA_API_KEY is not set` | `.env` is missing or you are not in the repo folder |
| `Drex HTTP 401` | wrong or revoked Nace key; create a new one in the console |
| `Drex HTTP 402` / insufficient credit | add credit (Billing) or redeem the event code |
| `429` / `529` | rate limit or busy; the client retries automatically. Lower `DREX_MAX_IN_FLIGHT` if it persists |
| `address already in use` | another app has port 8000: `PORT=8001 .venv/bin/pixeldrex-web` |
| `intern: command not found` | add `~/.local/bin` to your `PATH`, or re-run the `uv tool install` line |
| A scene looks like a blob | use a front-facing subject; side views are the known weak spot |
| A Life world freezes or turns to noise | worlds vary by run: run it again, or replay one from `worlds/` |
| NDI says `403` for a URL | that site blocks downloads; save the PDF and pass the local file instead |

## Windows

Use `python -m venv .venv`, then `.venv\Scripts\pip install -e .`, and run `.venv\Scripts\pixeldrex ...` /
`.venv\Scripts\pixeldrex-web`. Copy the env file with `copy .env.example .env`. Set the port with
`set PORT=8001` before starting the web app.
