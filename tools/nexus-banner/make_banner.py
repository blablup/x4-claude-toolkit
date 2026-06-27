#!/usr/bin/env python3
"""Generate a Nexus mod banner (default 1300x372) — the dark space-industrial X4 look.

A parameterised, cross-platform generalisation of the banner used for real X4 mods:
vertical gradient + starfield, an optional linked-node "network" motif with additive glow,
a left-edge veil for text legibility, and an auto-fitted two-tone title + subtitle + tagline.

Pure Pillow (no headless browser). Deterministic for a given --seed.

Examples:
  python make_banner.py --title DISTRIBUTION --title2 NETWORK \\
      --subtitle "Automated logistics for your X4 empire" \\
      --tagline "collect  ·  synchronise  ·  distribute by priority" \\
      --out dist/banner_1300x372.png
  python make_banner.py --title "Prospect Missions" --subtitle "Find-Resources, fixed" \\
      --no-motif --size 1300x372 --out banner.png
"""
from __future__ import annotations

import argparse
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# Font candidates per platform — first hit wins; PIL default is the last resort.
_BOLD = [
    "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
_REGULAR = [
    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def _find_font_path(bold: bool) -> str | None:
    import os
    for p in (_BOLD if bold else _REGULAR):
        if os.path.isfile(p):
            return p
    return None


def font(bold: bool, size: int):
    """A TrueType font at the requested size, or the PIL bitmap default."""
    path = _find_font_path(bold)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size)   # Pillow >= 10.1 accepts a size
    except TypeError:
        return ImageFont.load_default()


def hexcol(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def fit_font(draw, text, bold, start, max_w, min_size=18):
    """Largest font size (<= start) whose rendered *text* width fits *max_w*."""
    size = start
    while size > min_size:
        f = font(bold, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(bold, min_size)


def gradient_starfield(w, h, top, bot, rnd):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        row = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        for x in range(w):
            px[x, y] = row
    d = ImageDraw.Draw(img)
    for _ in range(int(w * h / 2200)):
        x, y, v = rnd.randint(0, w - 1), rnd.randint(0, h - 1), rnd.randint(30, 90)
        d.point((x, y), fill=(v, v, v + 10))
    return img


def network_motif(base, w, h, primary, accent, rnd):
    """Central amber hub + cyan satellites linked by glowing freight routes."""
    cx, cy = int(w * 0.68), int(h * 0.5)
    nodes = [(cx, cy, 16, accent)]
    sats = 7
    for i in range(sats):
        ang = (2 * math.pi * i / sats) + 0.3
        rad = rnd.randint(int(h * 0.32), int(h * 0.54))
        nx = int(cx + math.cos(ang) * rad)
        ny = int(cy + math.sin(ang) * rad * 0.62)
        nodes.append((nx, ny, rnd.randint(6, 11), primary))

    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for nx, ny, _, _ in nodes[1:]:
        gd.line((cx, cy, nx, ny), fill=(28, 90, 110), width=2)
    for i in range(1, len(nodes)):
        for j in range(i + 1, len(nodes)):
            if rnd.random() < 0.22:
                gd.line((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]),
                        fill=(18, 46, 60), width=1)
    base = ImageChops.add(base, glow.filter(ImageFilter.GaussianBlur(3)))

    draw = ImageDraw.Draw(base)
    for nx, ny, _, _ in nodes[1:]:
        draw.line((cx, cy, nx, ny), fill=(46, 120, 142), width=2)
    for nx, ny, rad, col in nodes:
        halo = Image.new("RGB", (w, h), (0, 0, 0))
        ImageDraw.Draw(halo).ellipse((nx - rad * 2, ny - rad * 2, nx + rad * 2, ny + rad * 2),
                                     fill=tuple(c // 3 for c in col))
        base = ImageChops.add(base, halo.filter(ImageFilter.GaussianBlur(rad)))
        draw = ImageDraw.Draw(base)
        draw.ellipse((nx - rad, ny - rad, nx + rad, ny + rad), fill=col)
        draw.ellipse((nx - rad // 2, ny - rad // 2, nx + rad // 2, ny + rad // 2),
                     fill=(255, 255, 255))
    return base


def main():
    ap = argparse.ArgumentParser(description="Generate a Nexus mod banner (Pillow).")
    ap.add_argument("--title", required=True, help="main title (first line)")
    ap.add_argument("--title2", default="", help="optional second title line (accent colour)")
    ap.add_argument("--subtitle", default="", help="one-line subtitle")
    ap.add_argument("--tagline", default="", help="small accent tagline under the subtitle")
    ap.add_argument("--out", required=True, help="output PNG path")
    ap.add_argument("--size", default="1300x372", help="WxH (default 1300x372, the Nexus header)")
    ap.add_argument("--primary", default="#4ac8e2", help="accent colour for title2/nodes (hex)")
    ap.add_argument("--accent", default="#f0a848", help="amber accent for bar/hub/tagline (hex)")
    ap.add_argument("--bg-top", default="#080e1a", help="gradient top (hex)")
    ap.add_argument("--bg-bottom", default="#03060c", help="gradient bottom (hex)")
    ap.add_argument("--seed", type=int, default=7, help="layout RNG seed (deterministic)")
    ap.add_argument("--no-motif", action="store_true", help="omit the network motif")
    args = ap.parse_args()

    w, h = (int(v) for v in args.size.lower().split("x"))
    primary, accent = hexcol(args.primary), hexcol(args.accent)
    bg_top, bg_bot = hexcol(args.bg_top), hexcol(args.bg_bottom)
    rnd = random.Random(args.seed)

    base = gradient_starfield(w, h, bg_top, bg_bot, rnd)
    if not args.no_motif:
        base = network_motif(base, w, h, primary, accent, rnd)

    # Left-edge veil so the text stays legible over the artwork.
    veil = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(veil)
    veil_end = w * 0.55
    for x in range(w):
        vd.line((x, 0, x, h), fill=max(0, int(190 * (1 - x / veil_end))))
    base = Image.composite(Image.new("RGB", (w, h), bg_bot), base, veil)
    draw = ImageDraw.Draw(base)

    # Text column: left margin .. start of the motif.
    margin = int(w * 0.054)
    col_w = int(w * 0.62) - margin
    two = bool(args.title2)
    t_size = int(h * 0.23)
    tf1 = fit_font(draw, args.title, True, t_size, col_w)
    tf2 = fit_font(draw, args.title2, True, t_size, col_w) if two else None
    line_h = int(t_size * 1.06)

    block_h = line_h * (2 if two else 1) + (76 if args.subtitle else 0) + (30 if args.tagline else 0)
    ty = max(int(h * 0.12), (h - block_h) // 2)
    tx = margin

    # Accent bar beside the title.
    bar_h = line_h * (2 if two else 1)
    draw.rectangle((tx, ty + 6, tx + 8, ty + bar_h - 6), fill=accent)
    txt_x = tx + 30
    draw.text((txt_x, ty), args.title, font=tf1, fill=(236, 244, 250))
    y = ty + line_h
    if two:
        draw.text((txt_x, y), args.title2, font=tf2, fill=primary)
        y += line_h
    y += 14
    if args.subtitle:
        draw.text((txt_x + 4, y), args.subtitle, font=font(True, max(18, int(h * 0.075))),
                  fill=(150, 170, 190))
        y += int(h * 0.097)
    if args.tagline:
        draw.text((txt_x + 4, y), args.tagline, font=font(False, max(14, int(h * 0.059))),
                  fill=accent)

    import os
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    base.save(args.out)
    print(f"wrote {args.out} ({w}x{h})")


if __name__ == "__main__":
    main()
