"""Export crisp PNG keyframes / strips from the real PixelDrex runs for the pitch deck."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "docs" / "gallery"
OUT = ROOT / "docs" / "deck" / "assets"
OUT.mkdir(parents=True, exist_ok=True)
BG = (13, 15, 26)


def frames(gif: Path) -> list[Image.Image]:
    im = Image.open(gif)
    out = []
    for i in range(im.n_frames):
        im.seek(i)
        out.append(im.convert("RGB"))
    return out


def scaled(img: Image.Image, size: int) -> Image.Image:
    return img.resize((size, size), Image.NEAREST)


def strip(gif: Path, k: int, size: int, gap: int = 10, start: float = 0.0) -> Image.Image:
    fr = frames(gif)
    n = len(fr)
    picks = [fr[min(n - 1, round(start * (n - 1) + i * (n - 1) * (1 - start) / (k - 1)))] for i in range(k)]
    s = Image.new("RGB", (k * size + (k - 1) * gap, size), BG)
    for i, f in enumerate(picks):
        s.paste(scaled(f, size), (i * (size + gap), 0))
    return s


def key(gif: Path, frac: float, size: int) -> Image.Image:
    fr = frames(gif)
    return scaled(fr[min(len(fr) - 1, round(frac * (len(fr) - 1)))], size)


def pixel_question() -> Image.Image:
    """The rocket sprite on a grid, with one pixel outlined: 'what color is this pixel?'"""
    f = key(G / "rocket.gif", 0.5, 32)  # 32x32 canvas, one cell per canvas pixel
    cell = 16
    img = f.resize((32 * cell, 32 * cell), Image.NEAREST)
    d = ImageDraw.Draw(img)
    for i in range(33):
        d.line([(i * cell, 0), (i * cell, 32 * cell)], fill=(0, 0, 0), width=1)
        d.line([(0, i * cell), (32 * cell, i * cell)], fill=(0, 0, 0), width=1)
    # find a red pixel (the rocket's nose) to highlight
    target = None
    for r in range(32):
        for c in range(32):
            px = f.getpixel((c, r))
            if px[0] > 200 and px[1] < 80 and px[2] < 80:
                target = (r, c)
                break
        if target:
            break
    r, c = target or (8, 16)
    d.rectangle([c * cell - 3, r * cell - 3, (c + 1) * cell + 3, (r + 1) * cell + 3], outline=(255, 204, 51), width=5)
    return img


def main() -> None:
    key(G / "life_forest_fire.gif", 0.45, 560).save(OUT / "hero_fire.png")
    strip(G / "life_forest_fire.gif", 6, 250).save(OUT / "strip_fire.png")
    strip(G / "life_zombies.gif", 6, 250).save(OUT / "strip_zombies.png")
    for name in ["ufo", "rocket", "cat_mouse", "sunrise"]:
        key(G / f"{name}.gif", 0.6, 320).save(OUT / f"scene_{name}.png")
    pixel_question().save(OUT / "pixel_question.png")
    key(G / "news_bird_flu.gif", 0.5, 420).save(OUT / "news_bird_flu.png")
    key(G / "news_wildfire.gif", 0.5, 420).save(OUT / "news_wildfire.png")
    ba = Image.open(G / "god_coral_before_after.png").convert("RGB")
    ba.save(OUT / "god_coral.png")
    for p in sorted(OUT.glob("*.png")):
        print(p.name, Image.open(p).size, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
