"""Benchmark: can a decision model paint pixel art better/faster/cheaper than LLMs writing pixels as text?

For each subject:
  - Drex: one request, 256 `choice` questions (one per pixel)
  - LLMs on DeepInfra: asked for the same 16x16 grid as JSON rows of palette letters
Measured: wall time, $ cost, valid-output rate, and a blind pairwise judgment by a vision LLM
(Qwen3-VL-235B) shown each pair in BOTH orders; a win needs both orders, otherwise it's a tie.

Run: .venv/bin/python bench/run.py
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw  # noqa: E402

from pixeldrex.drex import Drex  # noqa: E402
from pixeldrex.llm import DeepInfra  # noqa: E402
from pixeldrex.pixels import PALETTE, Painting, paint, png_b64  # noqa: E402

SUBJECTS = ["a red heart", "a yellow sun", "a rocket ship", "a cat face", "a green tree", "a house",
            "a fish", "a smiley face"]
LLMS = ["deepseek-ai/DeepSeek-V4-Flash", "moonshotai/Kimi-K3"]
JUDGE = "Qwen/Qwen3-VL-235B-A22B-Instruct"
N = 16
LETTERS = dict(zip(PALETTE, "WKgRpOYbGDSBNPl"))  # one letter per palette color
FROM_LETTER = {v: k for k, v in LETTERS.items()}
OUT = ROOT / "bench" / "results"


def llm_prompt(subject: str) -> str:
    legend = ", ".join(f"{v}={k}" for k, v in LETTERS.items())
    return (
        f"Draw {subject} as {N}x{N} pixel art, like a classic 8-bit sprite, on a white background.\n"
        f"Use only these palette letters: {legend}.\n"
        f'Reply with JSON only: {{"rows": [ {N} strings, each exactly {N} letters ]}}. Row 0 is the top.'
    )


RAW: dict = {}


def is_blank(p: Painting) -> bool:
    """A grid that is (almost) all background counts as a failed drawing even if it parses."""
    return sum(x != "white" for row in p.grid for x in row) < 8


def parse_grid(text: str) -> tuple[list[list[str]], bool]:
    """Return (grid, valid). Invalid output is padded/truncated so it can still be shown."""
    rows: list[str] = []
    try:
        m = re.search(r"\{.*\}", text, re.S)
        rows = json.loads(m.group(0))["rows"] if m else []
    except Exception:
        rows = re.findall(r"[A-Za-z]{8,}", text)
    valid = len(rows) == N and all(isinstance(r, str) and len(r) == N and all(ch in FROM_LETTER for ch in r)
                                   for r in rows)
    grid = []
    for r in range(N):
        row = rows[r] if r < len(rows) and isinstance(rows[r], str) else ""
        grid.append([FROM_LETTER.get(row[c], "white") if c < len(row) else "white" for c in range(N)])
    return grid, valid


async def judge_pair(di: DeepInfra, subject: str, a: Painting, b: Painting) -> int:
    """+1 if `a` wins in both orders, -1 if `b` wins both, 0 otherwise."""
    async def ask(first: Painting, second: Painting) -> str:
        txt = await di.chat(
            f"Both images are 16x16 pixel-art attempts at drawing: {subject}. Which one is the clearer, more "
            f"recognizable drawing of {subject}? Answer with just the number 1 or 2.",
            images=[png_b64(first.flat()), png_b64(second.flat())], model=JUDGE, max_tokens=5, temperature=0,
        )
        return "1" if "1" in txt else "2" if "2" in txt else "?"
    ab, ba = await asyncio.gather(ask(a, b), ask(b, a))
    if ab == "1" and ba == "2":
        return 1
    if ab == "2" and ba == "1":
        return -1
    return 0


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results: dict = {"subjects": SUBJECTS, "drex": {}, "llms": {m: {} for m in LLMS}, "judge": JUDGE}
    async with Drex() as drex, DeepInfra() as di:
        async def drex_one(s: str):
            t0 = time.perf_counter()
            p = await paint(drex, s, n=N)
            return s, p, time.perf_counter() - t0, None  # cost filled in from total tokens below

        async def llm_one(model: str, s: str):
            t0 = time.perf_counter()
            before = di.usage.cost_usd
            finish, usage = None, {}
            try:
                text, data = await di.chat(llm_prompt(s), model=model, max_tokens=16000, temperature=0.2, raw=True)
                finish, usage = data["choices"][0].get("finish_reason"), data.get("usage") or {}
            except Exception as e:  # count API failures as invalid output
                text = f"ERROR {e}"
            grid, valid = parse_grid(text)
            RAW[(model, s)] = {"finish_reason": finish, "usage": usage, "content": text}
            return model, s, Painting(grid), valid, time.perf_counter() - t0, usage.get("estimated_cost") or 0.0

        drex_res, *llm_res = await asyncio.gather(
            asyncio.gather(*(drex_one(s) for s in SUBJECTS)),
            *(asyncio.gather(*(llm_one(m, s) for s in SUBJECTS)) for m in LLMS),
        )
        drex_p = {}
        per_image_cost = drex.usage.cost_usd / len(SUBJECTS)  # all 8 requests are the same size
        for s, p, sec, _ in drex_res:
            drex_p[s] = p
            results["drex"][s] = {"seconds": round(sec, 2), "cost_usd": per_image_cost, "valid": True,
                                  "blank": is_blank(p)}
        llm_p = {m: {} for m in LLMS}
        for group in llm_res:
            for model, s, p, valid, sec, cost in group:
                llm_p[model][s] = p
                results["llms"][model][s] = {"seconds": round(sec, 2), "cost_usd": cost, "valid": valid,
                                             "blank": is_blank(p),
                                             "finish_reason": RAW[(model, s)]["finish_reason"]}

        judge_cost0 = di.usage.cost_usd
        verdicts = await asyncio.gather(*(judge_pair(di, s, drex_p[s], llm_p[m][s]) for m in LLMS for s in SUBJECTS))
        results["judge_cost_usd"] = di.usage.cost_usd - judge_cost0
    i = 0
    for m in LLMS:
        for s in SUBJECTS:
            results["llms"][m][s]["drex_vs_this"] = verdicts[i]  # +1 Drex wins, -1 LLM wins, 0 tie
            i += 1

    # summary table
    def agg(rows: dict) -> dict:
        v = list(rows.values())
        return {
            "avg_seconds": round(sum(x["seconds"] for x in v) / len(v), 2),
            "total_cost_usd": round(sum(x["cost_usd"] for x in v), 6),
            "valid_rate": sum(x["valid"] for x in v) / len(v),
            "drawn_rate": sum(x["valid"] and not x["blank"] for x in v) / len(v),
        }
    summary = {"Drex (drex-max-v1.1)": agg(results["drex"])}
    for m in LLMS:
        a = agg(results["llms"][m])
        vs = [x["drex_vs_this"] for x in results["llms"][m].values()]
        a["drex_wins"], a["llm_wins"], a["ties"] = vs.count(1), vs.count(-1), vs.count(0)
        summary[m] = a
    results["summary"] = summary
    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    (OUT / "llm_raw_outputs.json").write_text(json.dumps(
        {f"{m} | {s}": v for (m, s), v in RAW.items()}, indent=2))

    # side-by-side grid image
    cell, pad, label_h = 128, 8, 28
    cols = ["Drex"] + [m.split("/")[-1] for m in LLMS]
    W = 150 + len(cols) * (cell + pad)
    H = label_h + len(SUBJECTS) * (cell + pad)
    img = Image.new("RGB", (W, H), (24, 26, 40))
    d = ImageDraw.Draw(img)
    for j, c in enumerate(cols):
        d.text((150 + j * (cell + pad), 8), c, fill=(255, 204, 51))
    for i, s in enumerate(SUBJECTS):
        y = label_h + i * (cell + pad)
        d.text((8, y + cell // 2 - 6), s, fill=(230, 230, 240))
        ps = [drex_p[s]] + [llm_p[m][s] for m in LLMS]
        for j, p in enumerate(ps):
            img.paste(p.flat(cell // N), (150 + j * (cell + pad), y))
            if j > 0:
                r = results["llms"][LLMS[j - 1]][s]
                tag = "INVALID" if not r["valid"] else "BLANK" if r["blank"] else ""
                if tag:
                    d.text((150 + j * (cell + pad) + 4, y + 4), tag, fill=(255, 60, 90))
    img.save(OUT / "grid.png")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
