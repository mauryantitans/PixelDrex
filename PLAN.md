# PixelDrex — build plan

> **Note (end of day):** this is the plan written at 11:00. What was actually built grew past it — Drex Life, god mode
> (Intern), NDI documents, Keenable news, part-based 32×32 sprites — see the [README](README.md) for the final project and
> [docs/SUBMISSION.md](docs/SUBMISSION.md) for the submission text.

> **Every pixel is a decision.**
> Drex can't draw — it only answers multiple-choice questions. So we turned every pixel into a question.
> A 16×16 sprite is a swarm of 256 Drex decisions, one request, ~1 second. Then Drex decides how it moves.

- **Event:** Drexathon (Nace AI), Sat Nov 14 2026, Frontier Tower SF
- **Track:** 🎨 **Wildcard** (most creative / surprising use of Drex)
- **Team:** solo
- **Build window:** 11:00 → **3:00 PM PT hard deadline** (target: finalized by 2:45)
- **Deliverables:** public GitHub repo (open source) + presentation + optional demo URL, submitted at nace.ai/drexathon/submit, then **Finalize**

---

## 1. What we're building

A tool that turns **any idea, document or news headline into an animated 8-bit GIF — painted entirely by Drex.**

```
"a rocket launching at night"
        │
        ▼
 Director (DeepInfra LLM) ── writes a scene spec: background, sprites, how each moves
        │
        ▼
 Drex paints ─┬─ background: 16×16 (256 choice questions, 1 call) → refined to 32×32 (1024 questions, 2 calls)
              ├─ each sprite: 16×16, + 5 free variations sampled from Drex's probabilities → Drex Max judges best of 6
              └─ motion: ONE call answers "where is the sprite & how big in each of 12 frames?" (score questions)
        │
        ▼
 Compositor → animated GIF  (~6 Drex calls, ~1,600 decisions, ~6–9 s, ~1¢)
```

### Input modes
| Mode | Input | Partner / Nace tool it showcases |
|---|---|---|
| **Prompt** | "a cat chasing a mouse" | DeepInfra (director), Drex |
| **8-bit News** | today's headlines | **Keenable** search → one GIF per headline |
| **Doc → Storyboard** | any PDF (story, pitch deck, report) | **NDI** parses/splits it → one GIF per scene |
| **Agent** | a request to the animator agent | **Intern** (System 2 = DeepInfra, System 1 = Drex) calls our tool, checks the result, retries |

---

## 2. What's already proven (built before 11:00)

All numbers are real runs against the live APIs.

| Experiment | Result |
|---|---|
| Drex key + `drex-max-finance` / `drex-max-v1.1` | ✅ working; 184 ms model time for one question |
| 100-persona swarm + 4 compliance questions in **one** image request | ✅ 1.4 s, ~$0.0004 (shows 512-questions-per-call trick works) |
| **v1:** every pixel of every frame = a choice question | Recognisable hearts at 16×16 (1 call/frame, 2.3 s for 4 frames). Frames don't connect → flicker; chaining frames → drift/decay |
| **v2:** layers + Drex-decided motion | ✅ coherent animations. Sun rises (y 30→1), **rocket rises *and shrinks with distance* (unprompted)**, heart pulses big→small→big. 6 calls, ~1,573 decisions, 6–9 s, ~$0.01 per GIF |

Files: `pixeldrex/drex.py` (client), `pixeldrex/llm.py` (DeepInfra: chat, vision, FLUX), `pixeldrex/pixels.py` (engine), `scripts/scene.py`, `scripts/drex_gif.py` (v1, keep for the "before/after" slide).

---

## 3. How Drex is used (the technical core)

| Job | Drex question type | Per request |
|---|---|---|
| Paint a pixel | `choice` over a 14-color palette (+ `none` = transparent for sprites) | up to 512 pixels; 32×32 = 2 parallel calls |
| Refine 16→32 | same, with the 16×16 version attached as **Image 1** (guide) | 2 calls |
| Pick the best sprite | `choice` over "Image 1…Image 6" (Drex Max sees all candidates) | 1 call |
| Motion path | `score` per frame for x, y, size (11 position levels, 5 sizes). **Expected value ⇒ sub-pixel smooth motion** | 1 call for all frames |
| (stretch) Self-critique | `noul` "Is the subject recognisable?" on the finished GIF frame | 1 call |

Free variations: sampling from the per-pixel probability distributions gives new candidates **without extra API calls** — Drex's calibration is literally the creative randomness.

Limits we design around: 512 questions/request, 8 images/request, 4 MiB body, **8 requests in flight (free tier)** — client already enforces this.

---

## 4. Tool usage (finalists are picked on usage of Drex, Intern, NDI and partner tools)

| Tool | How it's used | Priority |
|---|---|---|
| **Drex** (Max v1.1) | Paints, judges, animates — every visual decision | MUST (done) |
| **Intern** (rule #1) | (a) Used as coding agent for part of the build — keep session logs in `intern_logs/`. (b) **Animator agent** mode: `intern -p --json` with System 2 on DeepInfra, System 1 = Drex; it calls `drexpix`, looks at the output, retries if unrecognisable | MUST |
| **DeepInfra** | Director LLM (prompt → scene spec JSON); Intern's System 2; the LLM side of the benchmark; vision judge for the benchmark | MUST |
| **Keenable** | 8-bit News mode: search headlines → director → GIFs | SHOULD (~30 min) |
| **NDI** | Doc → Storyboard: parse/split a PDF into scenes → GIFs | SHOULD (~45 min) |
| **Adobe Express** | Presentation deck + a poster/social card of the GIF gallery, made through the Adobe Express connector | SHOULD (end of day) |

---

## 5. The benchmark (the "numbers" slide)

**Question:** can a decision model paint better/faster/cheaper than a frontier LLM writing pixels as text?

- 8 fixed prompts (heart, sun, rocket, cat, tree, house, fish, smiley).
- **Drex:** 16×16 per-pixel `choice` (1 call each).
- **LLMs on DeepInfra:** same palette, asked to return a 16×16 grid as JSON (DeepSeek-V4-Flash + one bigger model, e.g. Kimi-K3 or Qwen3.8-Max).
- **Measure:** wall time, $ cost (DeepInfra returns `estimated_cost`), valid-output rate (malformed / wrong-size grids count as failures), and **recognisability** — a *blind* vision-LLM judge (Qwen3-VL-235B) picks which of the two images better shows the prompt. (Not Drex judging itself.)
- Output: `bench/results.json` + a side-by-side image grid for the slides.

---

## 6. Build order (solo, 11:00 → 2:45)

| Time | Task | Done when |
|---|---|---|
| 11:00–11:20 | Create public GitHub repo, first commit (no `.env`!), install Intern, run one tiny Intern task (e.g. write the pixel-cleanup filter) and save its log | repo URL exists, Intern ran once |
| 11:20–12:00 | **Engine polish:** remove stray pixels, lower sampling temperature, simpler backgrounds (flat bands / skip 32× refine for skies), test 2-sprite scene | 4 good demo GIFs |
| 12:00–12:35 | **Director** (DeepInfra): prompt → scene spec JSON; CLI `drexpix "prompt"` | any prompt → GIF in one command |
| 12:35–1:10 | **Web page** (FastAPI + one HTML file): textbox → live progress (background → sprites → motion) → GIF + stats (calls, decisions, time, ¢); gallery of past GIFs | demo-able in a browser |
| 1:10–1:40 | **Benchmark** Drex vs LLMs | numbers + comparison image |
| 1:40–2:05 | **Keenable** 8-bit News; then **NDI** Doc → Storyboard if time | at least one extra mode works |
| 2:05–2:20 | **Intern animator agent** mode | one agent run recorded |
| 2:20–2:40 | Slides (Adobe Express), README with GIFs, record backup demo video | everything pushed |
| **2:40–2:45** | **Submit form → Finalize** | ✅ |

Cut order if behind: NDI → Keenable → web page (fall back to CLI + gallery HTML). Never cut: engine, director, benchmark, Intern, submission.

---

## 7. Demo script (5 minutes)

1. **Hook (20 s):** "Drex can't draw. It can only answer multiple-choice questions. So we asked it 1,600 of them." → show rocket GIF.
2. **How (60 s):** one slide: pixel = choice question; 256 pixels = one request; motion = score questions → expected values → smooth movement. Show v1 (flicker) → v2 (smooth) before/after.
3. **Live (90 s):** audience shouts a prompt → GIF appears in ~10 s with live counter of decisions and cost.
4. **Modes (45 s):** 8-bit News (Keenable) + PDF storyboard (NDI) + Intern agent clip.
5. **Numbers (45 s):** Drex vs LLM table — time, cost, valid-output rate, judge win-rate.
6. **Close (20 s):** "Every pixel was a decision. ~1,600 decisions, ~1 cent." Fun fact: nobody told the rocket to shrink.

---

## 8. Risks & fallbacks

| Risk | Fallback |
|---|---|
| Drex 429/529 under load during live demo | client retries; pre-rendered gallery + backup video |
| Venue Wi-Fi dies | backup video + GIFs in the repo/slides |
| Some prompts paint poorly | director rewrites subjects into simple iconic shapes; demo uses tested prompts + one live one |
| Intern rule interpretation | ask organizer at start; keep Intern logs regardless |
| Running out of credits | each GIF ≈ 1¢; $35 credit is plenty — still cap benchmark size |
| Leaking keys | `.env` gitignored, `.env.example` committed; check `git status` before every push |

---

## 9. Submission checklist

- [ ] Public GitHub repo with README (what/how/numbers/GIFs/how to run), MIT license
- [ ] `.env` NOT in the repo (`git log -p | grep nace_sk_` returns nothing)
- [ ] Presentation (Adobe Express) — link or PDF
- [ ] Demo URL or video (optional)
- [ ] Team registered with organizer's code
- [ ] Form: title, explanation, track = Wildcard, presentation, repo link
- [ ] Code pushed **before** clicking **Finalize** — by 2:45

## 10. Open questions

1. Does "Build with Intern" require Intern as the coding agent, or is using it inside the product enough? → ask an organizer.
2. Exact Drex price per token (set `DREX_PRICE_PER_M` in `.env` from the Billing page) so cost numbers are exact.
3. Keenable: keyless public tier enough, or get a key from an organizer?
