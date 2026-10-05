#!/usr/bin/env python3
"""Render the README's quiet, looping river banner and a static fallback.

The artwork is drawn locally from shapes and color fields. It does not claim
to be a screenshot of the app. Run with: python3 docs/hero/render_water.py
"""

from pathlib import Path
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1200, 390
FRAMES = 18
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Light.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"


def background(phase: float) -> Image.Image:
    y, x = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)
    depth = y / HEIGHT
    current = 10 * np.sin(x / 102 + phase) + 4 * np.sin(x / 44 - phase)
    ripple = np.sin((y + current) / 12 + phase * 0.35)
    shimmer = np.sin((x + y * 1.4) / 110 - phase) * 2.5
    strength = np.clip((y - 90) / 180, 0, 1)
    light = ripple * 4.5 * strength + shimmer * strength
    left_shadow = 9 * np.clip((700 - x) / 700, 0, 1)
    rgb = np.stack(
        [
            17 + depth * 8 + light * 0.35 - left_shadow * 0.5,
            52 + depth * 24 + light - left_shadow,
            49 + depth * 26 + light * 1.25 - left_shadow,
        ],
        axis=-1,
    )
    return Image.fromarray(np.uint8(np.clip(rgb, 0, 255)), "RGB").convert("RGBA")


def frame(index: int) -> Image.Image:
    phase = 2 * math.pi * index / FRAMES
    image = background(phase)
    water = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(water)

    # Thin, long contours move gently; all phases meet at the loop boundary.
    for row in range(23):
        baseline = 135 + row * 12
        points = []
        for x in range(0, WIDTH + 9, 9):
            y = baseline + 4.8 * math.sin(x / 91 + phase + row * 0.43)
            y += 1.7 * math.sin(x / 29 - phase + row * 0.66)
            points.append((x, round(y)))
        alpha = 11 + (row % 5) * 4
        draw.line(points, fill=(183, 226, 204, alpha), width=2 if row % 4 == 0 else 1)

    # A few highlights suggest reflected light rather than a literal photo.
    for row in (5, 12, 19):
        baseline = 135 + row * 12
        start = int(710 + 130 * math.sin(phase + row))
        points = []
        for x in range(start, min(start + 270, WIDTH), 5):
            y = baseline + 4.8 * math.sin(x / 91 + phase + row * 0.43)
            points.append((x, round(y)))
        draw.line(points, fill=(220, 242, 221, 56), width=2)

    image = Image.alpha_composite(image, water)
    draw = ImageDraw.Draw(image)
    font_label = ImageFont.truetype(SANS, 18)
    font_quote = ImageFont.truetype(SERIF, 47)
    font_echo = ImageFont.truetype(SERIF, 31)
    font_credit = ImageFont.truetype(SERIF, 18)
    font_tagline = ImageFont.truetype(SANS, 17)
    draw.text((67, 39), "OCTODINING   /   好好吃饭", font=font_label, fill=(195, 226, 199, 255))
    draw.line((68, 83, 1132, 83), fill=(181, 219, 194, 70), width=1)
    draw.text((67, 107), "逝者如斯，而未尝往也；", font=font_quote, fill=(246, 247, 233, 255))
    draw.text((69, 181), "盈虚者如彼，而卒莫消长也。", font=font_echo, fill=(231, 238, 221, 255))
    draw.text((69, 243), "苏轼 ·《前赤壁赋》", font=font_credit, fill=(191, 220, 199, 255))
    draw.line((68, 307, 1132, 307), fill=(181, 219, 194, 60), width=1)
    draw.text((69, 332), "选择会变，认真吃饭这件事不变。", font=font_tagline, fill=(225, 236, 218, 255))
    return image.convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = [frame(i) for i in range(FRAMES)]
    images[0].save(OUT / "flowing-water.png", optimize=True)
    palette = [im.quantize(colors=96, method=Image.Quantize.MEDIANCUT) for im in images]
    palette[0].save(
        OUT / "flowing-water.gif",
        save_all=True,
        append_images=palette[1:],
        duration=115,
        loop=0,
        disposal=2,
        optimize=True,
    )
    print(OUT / "flowing-water.gif", (OUT / "flowing-water.gif").stat().st_size)


if __name__ == "__main__":
    main()
