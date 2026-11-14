"""Paint an animated scene with Drex: background + sprites painted once, motion decided by Drex.

Run: .venv/bin/python scripts/scene.py sunrise
"""
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from pixeldrex.drex import Drex  # noqa: E402
from pixeldrex.pixels import SpriteSpec, save_gif, scene_gif  # noqa: E402

SCENES = {
    "sunrise": dict(
        scene="a sunrise over green hills",
        background="a light blue sky over rolling green grass hills that fill the bottom third",
        sprites=[SpriteSpec("sun", "a round yellow sun with orange rays",
                            "rises from behind the hills at the bottom center up to the top center of the sky")],
    ),
    "ball": dict(
        scene="a ball bouncing across a room",
        background="a plain white wall with a brown wooden floor along the bottom quarter",
        sprites=[SpriteSpec("ball", "a shiny blue rubber ball",
                            "bounces from the far left to the far right, hitting the floor three times")],
    ),
    "rocket": dict(
        scene="a rocket launching into space",
        background="a dark navy night sky with a few white stars, and gray ground along the bottom",
        sprites=[SpriteSpec("rocket", "a white rocket with a red nose cone and an orange flame at the bottom",
                            "launches from the ground at the bottom center and flies straight up and out of the top")],
    ),
    "heart": dict(
        scene="a beating heart",
        background="a soft pink background",
        sprites=[SpriteSpec("heart", "a big red heart",
                            "stays in the center and pulses: it grows large, then shrinks small, then grows again")],
    ),
}


async def main(name: str) -> None:
    spec = SCENES[name]
    out = ROOT / "out" / "scenes"
    out.mkdir(parents=True, exist_ok=True)
    async with Drex() as drex:
        t0 = time.perf_counter()
        frames, meta = await scene_gif(drex, **spec)
        dt = time.perf_counter() - t0
    save_gif(frames, out / f"{name}.gif")
    sheet = Image.new("RGB", (frames[0].width * 6 // 2, frames[0].height // 2), "white")
    for i, f in enumerate(frames[::2][:6]):
        sheet.paste(f.resize((f.width // 2, f.height // 2), Image.NEAREST), (i * f.width // 2, 0))
    sheet.save(out / f"{name}_sheet.png")
    meta["sprites"][0].flat(10).save(out / f"{name}_sprite.png")
    meta["background16"].flat(10).save(out / f"{name}_bg16.png")
    meta["background"].flat(5).save(out / f"{name}_bg32.png")
    u = drex.usage.summary()
    tr = meta["tracks"][0]
    print(f"{name}: {dt:.1f}s, {u['calls']} Drex calls, {u['questions']} decisions, ${u['cost_usd']:.4f}")
    print("  track x:", [round(x, 1) for x in tr.xs])
    print("  track y:", [round(y, 1) for y in tr.ys])
    print("  size   :", [round(s, 1) for s in tr.sizes])


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "sunrise"))
