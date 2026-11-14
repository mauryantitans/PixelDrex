"""Run a Drex Life world from an idea and save it as a GIF.

Run: .venv/bin/python scripts/life_demo.py "a forest fire" --size 24 --steps 30
"""
import argparse, asyncio, json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pixeldrex.life import run_life
from pixeldrex.pixels import save_gif

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("idea"); ap.add_argument("--size", type=int, default=24); ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--temp", type=float, default=0.6); ap.add_argument("--name")
    a = ap.parse_args()
    t0 = time.perf_counter()
    def on_world(w): print("world:", json.dumps(w.to_dict(), indent=1)[:1500], flush=True)
    def on_frame(i, life, info):
        if i % 5 == 0 or i < 4:
            print(f"  step {i:3d} [{time.perf_counter()-t0:5.1f}s] asked {info['new_questions']:3d} new, "
                  f"reused {info['cached']:3d} | census {life.census()}", flush=True)
    life, frames, stats = await run_life(a.idea, n=a.size, steps=a.steps, temperature=a.temp,
                                         on_frame=on_frame, on_world=on_world)
    out = ROOT / "out" / "life"; out.mkdir(parents=True, exist_ok=True)
    name = a.name or a.idea.replace(" ", "_")[:30]
    save_gif(frames, out / f"{name}.gif", ms=150)
    d = stats["drex"]
    print(f"{out / (name + '.gif')}: {a.size}x{a.size} x {a.steps} steps = {life.cell_updates:,} cell decisions, "
          f"{life.asked:,} unique questions to Drex in {d['calls']} calls, {time.perf_counter()-t0:.1f}s, ${d['cost_usd']:.4f}")

asyncio.run(main())
