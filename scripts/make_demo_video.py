"""Stitch recorded web-app runs into one backup demo video with title cards.

Usage: .venv/bin/python scripts/make_demo_video.py out/videos docs/pixeldrex_demo.mp4
Expects demo_life_forest_fire.mp4, demo_life_news_wildfire.mp4, demo_scene_ufo.mp4 in the input folder
(recorded with Playwright from `pixeldrex-web`).
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 860
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CLIPS = [
    ("demo_life_forest_fire.mp4", "Drex Life: a forest fire",
     "Every cell asks Drex what it becomes, every step. Rules are plain English."),
    ("demo_life_news_wildfire.mp4", "Drex Life from this week's news: wildfire",
     "Keenable searches and reads the articles; every rule cites its sources."),
    ("demo_scene_ufo.mp4", "Scene: a ufo abducting a cow at night",
     "A director plans the scene; Drex paints every pixel and decides the motion."),
]


def card(path: Path, title: str, sub: str, kicker: str = "PIXELDREX · every pixel is a decision") -> None:
    img = Image.new("RGB", (W, H), (13, 15, 26))
    d = ImageDraw.Draw(img)
    d.text((90, 300), kicker, font=ImageFont.truetype(REG, 26), fill=(79, 209, 197))
    d.text((90, 350), title, font=ImageFont.truetype(BOLD, 52), fill=(255, 204, 51))
    d.text((90, 440), sub, font=ImageFont.truetype(REG, 28), fill=(200, 206, 230))
    img.save(path)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    tmp = src / "_build"
    tmp.mkdir(exist_ok=True)
    parts = []
    intro = tmp / "card_0.png"
    card(intro, "PixelDrex — backup demo", "Live runs of the web app, recorded Nov 14 2026 at Drexathon.")
    parts.append((intro, 3.0))
    for i, (clip, title, sub) in enumerate(CLIPS, 1):
        c = tmp / f"card_{i}.png"
        card(c, title, sub)
        parts.append((c, 2.5))
        parts.append((src / clip, None))
    inputs, filters = [], []
    for k, (p, dur) in enumerate(parts):
        if dur:
            inputs += ["-loop", "1", "-t", str(dur), "-i", str(p)]
        else:
            inputs += ["-i", str(p)]
        filters.append(f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
                       f"fps=25,format=yuv420p,setsar=1[v{k}]")
    concat = "".join(f"[v{k}]" for k in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[out]"
    run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(filters) + ";" + concat,
         "-map", "[out]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-movflags", "+faststart",
         str(dst)])
    print(dst)


if __name__ == "__main__":
    main()
