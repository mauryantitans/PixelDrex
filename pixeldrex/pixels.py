"""Drex Pixels engine: Drex paints pixel art one `choice` decision per pixel, judges, and animates.

Pieces:
  paint()     -> one grid, every pixel = one Drex choice question (<=512 per request, chunks above)
  sample()    -> extra variations for free by sampling from the returned probabilities
  judge()     -> Drex Max looks at up to 8 candidates and picks the best one
  refine()    -> paint again at higher resolution with the coarse version as a guide image
  motion()    -> one Drex call decides every frame's x/y/size via `score` questions (expected values = smooth)
  scene_gif() -> background layer + sprite layers + Drex-decided motion -> animated GIF
"""
from __future__ import annotations

import asyncio
import io
import random
from dataclasses import dataclass, field

from PIL import Image

from pixeldrex.drex import Drex, choice, image_to_b64, noul, score

PALETTE: dict[str, tuple[int, int, int]] = {
    "white": (255, 255, 255),
    "black": (20, 20, 24),
    "gray": (140, 140, 150),
    "red": (225, 40, 50),
    "pink": (250, 150, 180),
    "orange": (245, 140, 30),
    "yellow": (250, 210, 40),
    "brown": (130, 80, 40),
    "green": (40, 170, 80),
    "darkgreen": (20, 100, 50),
    "skyblue": (150, 205, 250),
    "blue": (40, 110, 230),
    "navy": (25, 35, 90),
    "purple": (140, 70, 200),
}
TRANSPARENT = "none"  # sprite background

Grid = list[list[str]]


@dataclass
class Painting:
    grid: Grid
    probs: list[list[dict[str, float]]] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.grid)

    def image(self, scale: int = 1, bg: tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        n = self.n
        img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        for r in range(n):
            for c in range(n):
                name = self.grid[r][c]
                if name != TRANSPARENT:
                    img.putpixel((c, r), PALETTE[name] + (255,))
        if scale > 1:
            img = img.resize((n * scale, n * scale), Image.NEAREST)
        return img

    def flat(self, scale: int = 1, bg=(255, 255, 255)) -> Image.Image:
        im = self.image(scale)
        base = Image.new("RGBA", im.size, bg + (255,))
        base.alpha_composite(im)
        return base.convert("RGB")


def png_b64(img: Image.Image, upscale_to: int = 256) -> str:
    if img.width < upscale_to:
        k = max(1, upscale_to // img.width)
        img = img.resize((img.width * k, img.height * k), Image.NEAREST)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return image_to_b64(buf.getvalue(), max_side=upscale_to)


def _pixel_questions(n: int, colors: list[str]) -> dict[str, dict]:
    crit = {c: None for c in colors}
    return {
        f"p_{r:02d}_{c:02d}": choice(
            f"What color is the pixel at row {r}, column {c}? (row 0 is the top, column 0 is the left, "
            f"the grid is {n}x{n})",
            crit,
        )
        for r in range(n)
        for c in range(n)
    }


async def paint(
    drex: Drex,
    description: str,
    *,
    n: int = 16,
    colors: list[str] | None = None,
    sprite: bool = False,
    guide: Image.Image | None = None,
    model: str = "drex-max-v1.1",
) -> Painting:
    """Paint one n x n image. sprite=True adds a transparent 'none' color for the background."""
    colors = list(colors or PALETTE)
    if sprite and TRANSPARENT not in colors:
        colors = [TRANSPARENT] + colors
    state = (
        f"You are painting a {n}x{n} pixel-art image, like classic 8-bit sprite art. "
        f"Subject: {description}. Use bold, simple, recognizable shapes. "
    )
    if sprite:
        state += (f"This is a sprite: draw only the subject, centered and filling most of the grid, and answer "
                  f"'{TRANSPARENT}' for every background pixel. ")
    images = None
    if guide is not None:
        state += ("Image 1 is a rough low-resolution sketch of the same picture: keep its layout and colors, "
                  "and add detail and cleaner edges.")
        images = [png_b64(guide)]
    answers = await drex.ask_many(state, _pixel_questions(n, colors), images=images, model=model)
    grid = [[answers[f"p_{r:02d}_{c:02d}"]["choice"] for c in range(n)] for r in range(n)]
    probs = [[answers[f"p_{r:02d}_{c:02d}"]["probabilities"] for c in range(n)] for r in range(n)]
    return Painting(grid, probs)


def cleanup(p: Painting, *, passes: int = 1, min_same: int = 2) -> Painting:
    """Remove stray pixels: a pixel with fewer than `min_same` same-colored 8-neighbours
    takes the most common neighbouring color."""
    grid = [row[:] for row in p.grid]
    n = len(grid)
    for _ in range(passes):
        new = [row[:] for row in grid]
        for r in range(n):
            for c in range(n):
                nb = [grid[rr][cc] for rr in range(r - 1, r + 2) for cc in range(c - 1, c + 2)
                      if (rr, cc) != (r, c) and 0 <= rr < n and 0 <= cc < n]
                if sum(x == grid[r][c] for x in nb) < min_same:
                    new[r][c] = max(set(nb), key=nb.count)
        grid = new
    return Painting(grid, p.probs)


def _where(r0: int, c0: int, t: int, n: int) -> str:
    v = ["top", "upper-middle", "lower-middle", "bottom"][min(3, int((r0 + t / 2) / n * 4))]
    h = ["left", "center-left", "center-right", "right"][min(3, int((c0 + t / 2) / n * 4))]
    return f"{v} {h}"


async def paint_tiled(
    drex: Drex,
    description: str,
    guide: "Painting | Image.Image",
    n: int,
    *,
    tile: int = 16,
    colors: list[str] | None = None,
    model: str = "drex-max-v1.1",
    reference: bool = False,
) -> Painting:
    """Paint an n x n image tile by tile. Each tile sees a zoomed crop of `guide` (Image 1)
    and the whole guide with the tile outlined (Image 2). One Drex call per tile, run in parallel."""
    from PIL import ImageDraw

    colors = list(colors or PALETTE)
    crit = {c: None for c in colors}
    g = guide.flat() if isinstance(guide, Painting) else guide.convert("RGB")
    gscale = g.width / n  # guide pixels per target pixel

    async def one(r0: int, c0: int) -> tuple[int, int, dict]:
        box = (round(c0 * gscale), round(r0 * gscale), round((c0 + tile) * gscale), round((r0 + tile) * gscale))
        resample = Image.LANCZOS if reference else Image.NEAREST
        crop = g.crop(box).resize((256, 256), resample)
        whole = g.resize((256, 256), resample)
        k = 256 / g.width
        ImageDraw.Draw(whole).rectangle(
            [box[0] * k, box[1] * k, box[2] * k - 1, box[3] * k - 1], outline=(255, 0, 0), width=4
        )
        state = (
            f"You are painting a detailed {n}x{n} pixel-art image of: {description}. "
            f"This request paints ONE {tile}x{tile} tile of it: rows {r0}-{r0 + tile - 1} and columns "
            f"{c0}-{c0 + tile - 1} of the full image (the {_where(r0, c0, tile, n)} part). "
            + (
                f"Image 1 is a zoom of exactly this tile from the reference picture. Pixel-art it: each pixel "
                f"takes the palette color that best matches that spot of Image 1, with clean flat color areas. "
                f"Image 2 is the whole reference picture with this tile outlined in red."
                if reference else
                f"Image 1 is a blurry low-resolution zoom of exactly this tile: keep its layout and colors, "
                f"but make the edges crisp and add fine detail that fits the subject. "
                f"Image 2 is the whole low-resolution picture with this tile outlined in red."
            )
        )
        qs = {
            f"p_{r:02d}_{c:02d}": choice(
                f"In this tile, what color is the pixel at tile row {r}, tile column {c}? "
                f"(tile row 0 is the tile's top edge, tile column 0 its left edge, the tile is {tile}x{tile})",
                crit,
            )
            for r in range(tile)
            for c in range(tile)
        }
        res = await drex.ask(state, qs, images=[png_b64(crop), png_b64(whole)], model=model)
        return r0, c0, res.answers

    results = await asyncio.gather(*(one(r0, c0) for r0 in range(0, n, tile) for c0 in range(0, n, tile)))
    grid = [["white"] * n for _ in range(n)]
    probs = [[{} for _ in range(n)] for _ in range(n)]
    for r0, c0, ans in results:
        for r in range(tile):
            for c in range(tile):
                a = ans[f"p_{r:02d}_{c:02d}"]
                grid[r0 + r][c0 + c] = a["choice"]
                probs[r0 + r][c0 + c] = a["probabilities"]
    return Painting(grid, probs)


async def pyramid(
    drex: Drex, description: str, *, sizes: tuple[int, ...] = (16, 32, 64), clean: bool = True, **kw
) -> list[Painting]:
    """Coarse-to-fine: paint the first size whole, then each larger size tile by tile from the previous."""
    levels = [await paint(drex, description, n=sizes[0], **kw)]
    if clean:
        levels[0] = cleanup(levels[0])
    for n in sizes[1:]:
        nxt = await paint_tiled(drex, description, levels[-1], n, **kw)
        levels.append(cleanup(nxt) if clean else nxt)
    return levels


def sample(p: Painting, k: int, *, temperature: float = 1.0, seed: int = 0) -> list[Painting]:
    """k variations of a painting, drawn from Drex's per-pixel probabilities (no extra API calls)."""
    rnd = random.Random(seed)
    out = []
    for _ in range(k):
        grid = []
        for row in p.probs:
            new_row = []
            for dist in row:
                names = list(dist)
                w = [max(dist[x], 1e-9) ** (1 / temperature) for x in names]
                new_row.append(rnd.choices(names, weights=w)[0])
            grid.append(new_row)
        out.append(Painting(grid, p.probs))
    return out


async def judge(drex: Drex, description: str, candidates: list[Painting]) -> tuple[int, dict[str, float]]:
    """Drex Max looks at up to 8 candidates and picks the one that best shows the description."""
    cands = candidates[:8]
    labels = {f"image_{i + 1}": f"Image {i + 1}" for i in range(len(cands))}
    r = await drex.ask(
        f"These are {len(cands)} candidate pixel-art drawings of: {description}.",
        {"best": choice("Which image is the clearest, most recognizable drawing of the subject?", labels)},
        images=[png_b64(c.flat()) for c in cands],
    )
    best = r.pick("best")
    return int(best.split("_")[1]) - 1, r.probs("best")


async def refine(drex: Drex, description: str, coarse: Painting, n: int, **kw) -> Painting:
    """Paint at n x n using the (upscaled) coarse painting as the guide image."""
    return await paint(drex, description, n=n, guide=coarse.flat(), **kw)


async def best_painting(drex: Drex, description: str, *, n: int = 16, k: int = 6, **kw) -> Painting:
    """Paint once, sample k-1 variations from the probabilities, let Drex judge the best."""
    base = await paint(drex, description, n=n, **kw)
    cands = [base] + sample(base, k - 1, temperature=0.6)
    idx, _ = await judge(drex, description, cands)
    return cands[idx]


# ---------------------------------------------------------------- motion
@dataclass
class Track:
    xs: list[float]  # sprite center, 0..W-1
    ys: list[float]
    sizes: list[float]  # sprite size in canvas pixels


async def motion(
    drex: Drex, scene: str, sprite_name: str, motion_desc: str, *, frames: int, canvas: int, steps: int = 11
) -> Track:
    """One Drex call decides the sprite's position and size in every frame (score = expected value)."""
    pos_levels = [f"{round(i * (canvas - 1) / (steps - 1))}" for i in range(steps)]
    x_levels = [f"column {v} ({'far left' if i == 0 else 'far right' if i == steps - 1 else 'between'})"
                for i, v in enumerate(pos_levels)]
    y_levels = [f"row {v} ({'top' if i == 0 else 'bottom' if i == steps - 1 else 'between'})"
                for i, v in enumerate(pos_levels)]
    size_levels = ["tiny", "small", "medium", "large", "huge"]
    qs: dict[str, dict] = {}
    for f in range(frames):
        when = f"in frame {f + 1} of {frames} ({f / max(frames - 1, 1):.0%} through the animation)"
        qs[f"x_{f:02d}"] = score(f"Where is the center of the {sprite_name} horizontally {when}?", x_levels)
        qs[f"y_{f:02d}"] = score(f"Where is the center of the {sprite_name} vertically {when}?", y_levels)
        qs[f"s_{f:02d}"] = score(f"How big is the {sprite_name} {when}?", size_levels)
    state = (f"An animated {canvas}x{canvas} pixel-art scene: {scene}. The {sprite_name} moves like this: "
             f"{motion_desc}. Row 0 is the top of the canvas and column 0 is the left edge.")
    r = await drex.ask(state, qs)
    to_px = (canvas - 1) / (steps - 1)
    size_px = [0.2, 0.35, 0.5, 0.65, 0.85]  # fraction of canvas
    xs = [r.score(f"x_{f:02d}") * to_px for f in range(frames)]
    ys = [r.score(f"y_{f:02d}") * to_px for f in range(frames)]

    def size_at(f: int) -> float:
        e = r.score(f"s_{f:02d}")
        lo = int(e)
        hi = min(lo + 1, len(size_px) - 1)
        return canvas * (size_px[lo] + (size_px[hi] - size_px[lo]) * (e - lo))

    return Track(xs, ys, [size_at(f) for f in range(frames)])


def compose(background: Painting, sprites: list[tuple[Painting, Track]], frames: int, scale: int) -> list[Image.Image]:
    canvas = background.n
    bg = background.flat()
    out = []
    for f in range(frames):
        frame = bg.convert("RGBA")
        for sp, tr in sprites:
            size = max(2, round(tr.sizes[f]))
            img = sp.image().resize((size, size), Image.NEAREST)
            x = round(tr.xs[f] - size / 2)
            y = round(tr.ys[f] - size / 2)
            layer = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            layer.paste(img, (x, y), img)
            frame.alpha_composite(layer)
        out.append(frame.convert("RGB").resize((canvas * scale, canvas * scale), Image.NEAREST))
    return out


def save_gif(frames: list[Image.Image], path, ms: int = 110) -> None:
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=False)


@dataclass
class SpriteSpec:
    name: str
    look: str
    motion: str


async def scene_gif(
    drex: Drex,
    *,
    scene: str,
    background: str,
    sprites: list[SpriteSpec],
    frames: int = 12,
    canvas: int = 32,
    sprite_px: int = 16,
    k: int = 6,
) -> tuple[list[Image.Image], dict]:
    """Background painted once (refined 16->32), sprites painted once (best of k), Drex decides motion."""
    bg_task = paint(drex, f"background only, no characters: {background}", n=16)
    sprite_tasks = [best_painting(drex, s.look, n=sprite_px, k=k, sprite=True) for s in sprites]
    motion_tasks = [motion(drex, scene, s.name, s.motion, frames=frames, canvas=canvas) for s in sprites]
    bg16, *rest = await asyncio.gather(bg_task, *sprite_tasks, *motion_tasks)
    sprite_ps, tracks = rest[: len(sprites)], rest[len(sprites):]
    bg = await refine(drex, f"background only, no characters: {background}", bg16, n=canvas)
    frames_out = compose(bg, list(zip(sprite_ps, tracks)), frames, scale=max(1, 320 // canvas))
    meta = {"background16": bg16, "background": bg, "sprites": sprite_ps, "tracks": tracks}
    return frames_out, meta
