"""Drex paints pixel-art GIFs: every pixel of every frame is one Drex `choice` question.

A 16x16 frame = 256 questions = ONE Drex request. An 8-frame GIF = 8 requests, run in parallel.

Run: .venv/bin/python scripts/drex_gif.py "a red heart" --frames 8
"""
import argparse
import asyncio
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from pixeldrex.drex import Drex, choice, image_to_b64  # noqa: E402

PALETTE = {
    "white": (255, 255, 255),
    "black": (20, 20, 20),
    "red": (225, 40, 50),
    "yellow": (250, 210, 40),
    "blue": (40, 110, 230),
    "green": (40, 170, 80),
    "orange": (245, 140, 30),
    "skyblue": (150, 205, 250),
}
CRITERIA = {name: None for name in PALETTE}
LETTER = {"white": ".", "black": "K", "red": "R", "yellow": "Y", "blue": "B", "green": "G", "orange": "O", "skyblue": "S"}
LEGEND = ", ".join(f"{v}={k}" for k, v in LETTER.items())


def png_bytes(img: Image.Image) -> bytes:
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def frame_questions(n: int) -> dict:
    qs = {}
    for r in range(n):
        for c in range(n):
            qs[f"p_{r:02d}_{c:02d}"] = choice(
                f"What color is the pixel at row {r}, column {c}? "
                f"(row 0 is the top, column 0 is the left, the grid is {n}x{n})",
                CRITERIA,
            )
    return qs


def render(answers: dict, n: int, scale: int, sample: bool, rnd: random.Random) -> Image.Image:
    img = Image.new("RGB", (n, n))
    for r in range(n):
        for c in range(n):
            a = answers[f"p_{r:02d}_{c:02d}"]
            if sample:  # sample from Drex's distribution instead of argmax
                names, ps = zip(*a["probabilities"].items())
                name = rnd.choices(names, weights=ps)[0]
            else:
                name = a["choice"]
            img.putpixel((c, r), PALETTE[name])
    return img.resize((n * scale, n * scale), Image.NEAREST)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("subject", nargs="?", default="a red heart")
    ap.add_argument("--motion", default="pulses: it grows bigger then smaller again")
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--size", type=int, default=16)
    ap.add_argument("--scale", type=int, default=16)
    ap.add_argument("--sample", action="store_true", help="sample pixels from the probabilities")
    ap.add_argument("--model", default="drex-max-v1.1")
    ap.add_argument("--name", default=None)
    ap.add_argument("--chain", action="store_true", help="show Drex the previous frame (image + grid) for smooth motion")
    args = ap.parse_args()

    n = args.size
    qs = frame_questions(n)

    def state(i: int) -> str:
        return (
            f"You are drawing frame {i + 1} of {args.frames} of a looping {n}x{n} pixel-art animation "
            f"on a plain white background. Subject: {args.subject}. Motion: {args.motion}. "
            f"Frame {i + 1} is {i / args.frames:.0%} of the way through the loop. "
            f"Use bold, simple shapes centered in the grid, like classic 8-bit sprite art."
        )

    rnd = random.Random(0)
    async with Drex(model=args.model) as drex:
        t0 = time.perf_counter()
        if not args.chain:
            results = await asyncio.gather(*(drex.ask(state(i), qs) for i in range(args.frames)))
            frames = [render(r.answers, n, args.scale, args.sample, rnd) for r in results]
        else:
            results, frames = [], []
            for i in range(args.frames):
                if not frames:
                    r = await drex.ask(state(i), qs)
                else:
                    prev = results[-1].answers
                    grid = "\n".join(
                        " ".join(LETTER[prev[f"p_{rr:02d}_{cc:02d}"]["choice"]] for cc in range(n)) for rr in range(n)
                    )
                    st = (state(i) + "\n\nImage 1 is the previous frame. Keep the same subject, colors and style, "
                          "and change only what the motion requires for this frame. Previous frame as a grid "
                          f"(row 0 first; {LEGEND}):\n{grid}")
                    r = await drex.ask(st, qs, images=[image_to_b64(png_bytes(frames[-1]), max_side=256)])
                results.append(r)
                frames.append(render(r.answers, n, args.scale, args.sample, rnd))
        dt = time.perf_counter() - t0
    out = ROOT / "out" / "gifs"
    out.mkdir(parents=True, exist_ok=True)
    name = args.name or args.subject.replace(" ", "_")[:40]
    gif = out / f"{name}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=120, loop=0)
    # contact sheet for quick viewing
    sheet = Image.new("RGB", (frames[0].width * len(frames), frames[0].height), "white")
    for i, f in enumerate(frames):
        sheet.paste(f, (i * f.width, 0))
    sheet.save(out / f"{name}_sheet.png")
    (out / f"{name}.json").write_text(json.dumps([r.answers for r in results]))

    u = drex.usage.summary()
    print(f"{gif}: {args.frames} frames x {len(qs)} pixels = {args.frames * len(qs)} Drex decisions "
          f"in {dt:.1f}s, {u['input_tokens']} tokens, ~${u['cost_usd']:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
