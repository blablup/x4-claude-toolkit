#!/usr/bin/env python3
"""Normalize user-supplied screenshots into a Nexus-ready gallery folder.

Lets you drop any images (PNG/JPG/WebP/...) and get clean, web-sized, metadata-stripped,
sequentially-numbered files for upload — in a deterministic gallery order. Pure Pillow, so it
runs the same on Linux/macOS/Windows.

Inputs may be files, directories (scanned, sorted by name), or globs. Order = the order given,
then alphabetical within a directory.

Example:
  python prep_images.py shots/ extra.png --out dist/images --prefix gallery_ --max-width 1920
"""
from __future__ import annotations

import argparse
import glob
import os

from PIL import Image, ImageOps

EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff")


def expand_inputs(items: list[str]) -> list[str]:
    out: list[str] = []
    for it in items:
        if os.path.isdir(it):
            out += sorted(os.path.join(it, f) for f in os.listdir(it)
                          if f.lower().endswith(EXTS))
        elif any(ch in it for ch in "*?["):
            out += sorted(glob.glob(it))
        elif os.path.isfile(it):
            out.append(it)
        else:
            print(f"  [skip] not found: {it}")
    return out


def main():
    ap = argparse.ArgumentParser(description="Prepare screenshots for a Nexus mod gallery.")
    ap.add_argument("inputs", nargs="+", help="image files, directories, or globs (order = gallery order)")
    ap.add_argument("--out", required=True, help="output directory (created)")
    ap.add_argument("--prefix", default="gallery_", help="output filename prefix (default gallery_)")
    ap.add_argument("--max-width", type=int, default=1920, help="downscale wider images (default 1920)")
    ap.add_argument("--max-height", type=int, default=1080, help="downscale taller images (default 1080)")
    ap.add_argument("--format", choices=("keep", "png", "jpg"), default="keep",
                    help="output format (default keep; RGBA is flattened for jpg)")
    ap.add_argument("--quality", type=int, default=90, help="JPEG quality (default 90)")
    ap.add_argument("--start", type=int, default=1, help="first index (default 1)")
    args = ap.parse_args()

    files = expand_inputs(args.inputs)
    if not files:
        print("No images found."); raise SystemExit(1)
    os.makedirs(args.out, exist_ok=True)

    idx = args.start
    print(f"Gallery order -> {args.out}")
    for src in files:
        try:
            im = Image.open(src)
            im = ImageOps.exif_transpose(im)          # honor rotation, then drop EXIF
        except Exception as e:                          # noqa: BLE001 — report, skip, continue
            print(f"  [skip] {src}: {type(e).__name__} {e}"); continue

        fmt = args.format
        if fmt == "keep":
            fmt = "jpg" if (im.format or "").upper() in ("JPEG", "JPG") else "png"
        if fmt == "jpg" and im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        elif im.mode == "P":
            im = im.convert("RGBA")

        w, h = im.size
        scale = min(args.max_width / w, args.max_height / h, 1.0)
        if scale < 1.0:
            im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)

        ext = "jpg" if fmt == "jpg" else "png"
        dst = os.path.join(args.out, f"{args.prefix}{idx:02d}.{ext}")
        save_kw = {"quality": args.quality, "optimize": True} if fmt == "jpg" else {"optimize": True}
        im.save(dst, **save_kw)
        kb = os.path.getsize(dst) // 1024
        print(f"  {idx:02d}. {os.path.basename(dst)}  {im.size[0]}x{im.size[1]}  {kb} KB  (from {os.path.basename(src)})")
        idx += 1

    print(f"Done: {idx - args.start} image(s). Upload them to Nexus in this numbered order.")


if __name__ == "__main__":
    main()
