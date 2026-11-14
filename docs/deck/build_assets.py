"""Export crisp PNG keyframes / strips from the real PixelDrex runs for the pitch deck."""
from pathlib import Path

from PIL import Image

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


def strip(gif: Path, k: int, size: int, gap: int = 10, start: float = 0.0, end: float = 1.0) -> Image.Image:
    fr = frames(gif)
    n = len(fr)
    idx = [round((start + (end - start) * i / (k - 1)) * (n - 1)) for i in range(k)]
    s = Image.new("RGB", (k * size + (k - 1) * gap, size), BG)
    for i, j in enumerate(idx):
        s.paste(scaled(fr[j], size), (i * (size + gap), 0))
    return s


def key(gif: Path, frac: float, size: int) -> Image.Image:
    fr = frames(gif)
    return scaled(fr[min(len(fr) - 1, round(frac * (len(fr) - 1)))], size)


def main() -> None:
    key(G / "life_forest_fire.gif", 0.5, 640).save(OUT / "hero_fire.png")
    strip(G / "life_forest_fire.gif", 6, 270, end=0.9).save(OUT / "strip_fire.png")
    strip(G / "life_zombies.gif", 6, 270, end=0.9).save(OUT / "strip_zombies.png")
    strip(G / "ufo.gif", 5, 330).save(OUT / "strip_ufo.png")
    strip(G / "rocket.gif", 5, 330).save(OUT / "strip_rocket.png")
    Image.open(G / "parts_vs_colors.png").convert("RGB").save(OUT / "parts_vs_colors.png")
    key(G / "news_bird_flu.gif", 0.5, 420).save(OUT / "news_bird_flu.png")
    Image.open(G / "god_coral_before_after.png").convert("RGB").save(OUT / "god_coral.png")
    for p in sorted(OUT.glob("*.png")):
        print(p.name, Image.open(p).size, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
