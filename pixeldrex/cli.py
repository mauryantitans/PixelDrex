"""`pixeldrex "an idea"` -> the director writes a scene, Drex paints and animates it, you get a GIF.

Examples:
  pixeldrex "a cat chasing a mouse"
  pixeldrex "a ufo abducting a cow" --frames 20
  pixeldrex "fireworks over a city" --spec-only          # just show the director's scene spec
  pixeldrex --spec out/gallery/<run>/spec.json            # re-paint a saved spec, no director call
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image

from pixeldrex.director import SceneSpec, direct
from pixeldrex.drex import Drex
from pixeldrex.llm import DeepInfra
from pixeldrex.pixels import save_gif, scene_gif

ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "out" / "gallery"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "scene"


class Progress:
    def __init__(self, quiet: bool = False):
        self.t0 = time.perf_counter()
        self.quiet = quiet

    def log(self, msg: str) -> None:
        if not self.quiet:
            print(f"  [{time.perf_counter() - self.t0:5.1f}s] {msg}", flush=True)

    def on_event(self, kind: str, payload: dict) -> None:
        if kind == "background":
            self.log("background painted (256 pixel decisions)")
        elif kind == "sprite":
            self.log(f"sprite '{payload['name']}' painted 3 ways, judged best of 6")
        elif kind == "motion":
            tr = payload["result"]
            self.log(f"motion for '{payload['name']}' decided: "
                     f"({tr.xs[0]:.0f},{tr.ys[0]:.0f}) -> ({tr.xs[-1]:.0f},{tr.ys[-1]:.0f}), "
                     f"size {tr.sizes[0]:.0f} -> {tr.sizes[-1]:.0f}")
        elif kind == "done":
            self.log(f"composited {payload['frames']} frames")


async def run(
    idea: str | None,
    *,
    spec_path: str | None = None,
    frames: int = 16,
    ms: int = 90,
    outline: bool = True,
    spec_only: bool = False,
    quiet: bool = False,
    on_event=None,
) -> dict:
    """Full pipeline. Returns a dict with the spec, output paths and stats (also used by the web app)."""
    prog = Progress(quiet)
    t_start = time.perf_counter()
    director_stats = None

    if spec_path:
        spec = SceneSpec.from_dict(json.loads(Path(spec_path).read_text()))
        idea = idea or spec.scene
        prog.log(f"loaded spec '{spec.title}'")
    else:
        async with DeepInfra() as di:
            prog.log(f"director is planning: {idea!r}")
            spec = await direct(di, idea)
            director_stats = di.usage.summary()
        prog.log(f"director: '{spec.title}' with {len(spec.sprites)} sprite(s): "
                 + ", ".join(s.name for s in spec.sprites))
    if on_event:
        on_event("spec", {"spec": spec.to_dict()})
    if spec_only:
        return {"spec": spec.to_dict(), "director": director_stats}

    def events(kind: str, payload: dict) -> None:
        prog.on_event(kind, payload)
        if on_event:
            on_event(kind, payload)

    async with Drex() as drex:
        gif_frames, meta = await scene_gif(
            drex, scene=spec.scene, background=spec.background, sprites=spec.sprites,
            frames=frames, outline=outline, on_event=events,
        )
    total_s = time.perf_counter() - t_start

    run_dir = GALLERY / f"{datetime.now():%Y%m%d-%H%M%S}-{slugify(spec.title)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    save_gif(gif_frames, run_dir / "anim.gif", ms=ms)
    w, h = gif_frames[0].size
    picks = gif_frames[:: max(1, len(gif_frames) // 6)][:6]
    sheet = Image.new("RGB", (w // 2 * len(picks), h // 2), "white")
    for i, f in enumerate(picks):
        sheet.paste(f.resize((w // 2, h // 2), Image.NEAREST), (i * w // 2, 0))
    sheet.save(run_dir / "sheet.png")
    for j, sp in enumerate(meta["sprites"]):
        sp.flat(10, bg=(205, 210, 220)).save(run_dir / f"sprite{j}.png")
    meta["background"].flat(10).save(run_dir / "background.png")

    drex_stats = drex.usage.summary()
    stats = {
        "idea": idea,
        "spec": spec.to_dict(),
        "frames": len(gif_frames),
        "seconds": round(total_s, 1),
        "drex": drex_stats,
        "director": director_stats,
        "tracks": [{"x": [round(v, 2) for v in t.xs], "y": [round(v, 2) for v in t.ys],
                    "size": [round(v, 2) for v in t.sizes]} for t in meta["tracks"]],
        "dir": str(run_dir.relative_to(ROOT)),
        "gif": str((run_dir / "anim.gif").relative_to(ROOT)),
    }
    (run_dir / "spec.json").write_text(json.dumps(spec.to_dict(), indent=2))
    (run_dir / "stats.json").write_text(json.dumps(stats, indent=2))
    return stats


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="pixeldrex", description="Drex paints and animates your idea as a pixel-art GIF.")
    ap.add_argument("idea", nargs="?", help="what to animate, e.g. 'a cat chasing a mouse'")
    ap.add_argument("--spec", help="paint a saved scene spec JSON instead of calling the director")
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--ms", type=int, default=90, help="milliseconds per frame")
    ap.add_argument("--no-outline", action="store_true")
    ap.add_argument("--spec-only", action="store_true", help="print the director's scene spec and stop")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    args = ap.parse_args(argv)
    if not args.idea and not args.spec:
        ap.error("give an idea, e.g. pixeldrex \"a cat chasing a mouse\", or --spec FILE")

    print(f"PixelDrex: {args.idea or args.spec}", flush=True)
    res = asyncio.run(run(args.idea, spec_path=args.spec, frames=args.frames, ms=args.ms,
                          outline=not args.no_outline, spec_only=args.spec_only, quiet=args.json))
    if args.json or args.spec_only:
        print(json.dumps(res, indent=2))
        return
    d = res["drex"]
    print(f"\n  GIF: {res['gif']}")
    print(f"  {d['questions']:,} Drex decisions in {d['calls']} calls · {res['seconds']}s total · "
          f"Drex ≈ ${d['cost_usd']:.4f}"
          + (f" · director ${res['director']['cost_usd']:.5f}" if res.get("director") else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
