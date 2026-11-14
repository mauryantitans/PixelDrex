"""Compare background painting: pixel questions only vs pixel x row fusion (same single request)."""
import asyncio, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
from pixeldrex.drex import Drex
from pixeldrex.pixels import paint_background, cleanup

BGS = [
    "a light gray wall at the top half and a brown wooden floor at the bottom half",
    "a black night sky with a few white stars over dark green grass along the bottom quarter",
    "a light blue sky above a dark blue sea, the horizon a little below the middle",
    "an orange sunset sky fading to purple at the top, over a black city skyline along the bottom third",
]

async def main():
    async with Drex() as drex:
        outs = await asyncio.gather(*(paint_background(drex, d) for d in BGS))  # pixel x row fusion
        raw = await asyncio.gather(*(paint_background(drex, d, row_weight=0.0) for d in BGS))  # pixels only
    s = 160
    sheet = Image.new("RGB", (s * 2 + 8, (s + 8) * len(BGS)), (170, 170, 170))
    for i, (a, b) in enumerate(zip(raw, outs)):
        sheet.paste(cleanup(a, passes=2).flat(s // 16), (0, i * (s + 8)))
        sheet.paste(cleanup(b, passes=2).flat(s // 16), (s + 8, i * (s + 8)))
    out = ROOT / "out" / "bg_test.png"; sheet.save(out); print(out)

asyncio.run(main())
