# nexus-banner

A small, dependency-light banner generator for X4 mod pages (Nexus / Steam). Pure
[Pillow](https://python-pillow.org/) — no headless browser — so it runs the same on Linux,
macOS and Windows. Produces the dark "space-industrial" look used by real X4 mods.

Default size is **1300×372** (the Nexus mod-page header). Override with `--size WxH`
(e.g. `1280x720` for a hero/thumbnail).

## Run

```bash
# via uv (no global install needed — uv pulls Pillow on the fly):
uv run --with pillow python tools/nexus-banner/make_banner.py \
    --title DISTRIBUTION --title2 NETWORK \
    --subtitle "Automated logistics for your X4 empire" \
    --tagline "collect · synchronise · distribute by priority" \
    --out dist/banner_1300x372.png

# or with a system Pillow:
python3 tools/nexus-banner/make_banner.py --title "Prospect Missions" \
    --subtitle "Find-Resources guild missions, made playable" --out banner.png
```

## Options

| Flag | Default | Meaning |
|------|---------|---------|
| `--title` | (required) | main title line |
| `--title2` | — | optional second line (drawn in `--primary`) |
| `--subtitle` | — | one-line subtitle |
| `--tagline` | — | small accent tagline |
| `--out` | (required) | output PNG path (dirs created) |
| `--size` | `1300x372` | `WxH` |
| `--primary` | `#4ac8e2` | accent for title2 + nodes (hex) |
| `--accent` | `#f0a848` | amber for the bar / hub / tagline (hex) |
| `--bg-top` / `--bg-bottom` | `#080e1a` / `#03060c` | gradient (hex) |
| `--seed` | `7` | deterministic layout RNG |
| `--no-motif` | off | omit the linked-node network motif |

The title font auto-fits to the left text column, so long titles shrink instead of overflowing.
Fonts are auto-discovered (Liberation/DejaVu/Arial across OSes) with a PIL fallback.
