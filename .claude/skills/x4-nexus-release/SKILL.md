---
name: x4-nexus-release
description: Generate the Nexus Mods release package for an X4 mod — a BBCode mod-page description, resolved requirement links, a changelog, and a 1300x372 banner — from the mod's own files. Use when the user wants to publish/update a mod on Nexus, write its mod page, or make a banner.
allowed-tools: Read, Write, Glob, Grep, Bash
---

Produce everything needed for an X4 mod's **Nexus Mods** page, derived from the mod's own
files — never invent features. Output goes to the mod's `dist/` folder.

**Inputs:** the mod directory (must have `content.xml`). Read also `README.md`, `CHANGELOG.md`,
and `docs/` if present. Confirm before overwriting existing `dist/` artifacts.

## 1. Gather facts (do this first — no fabrication)
From `content.xml`: `id`, `name`, `version` (integer → display as `M.m.p`, e.g. 120 → 1.2.0),
`description`, `author`, `save` flag, and every `<dependency>`. From `README.md` / `CHANGELOG.md`
/ `docs/`: the real feature list, the latest changelog, options/menu, languages (check `t/` for
`l044`=EN, `l049`=DE, etc.), and any known compatibility notes.

## 2. Resolve requirement links (Nexus API)
Each `<dependency>` becomes a requirement line with a real Nexus URL where possible. Resolve via
the bundled client (needs `X4_NEXUS_KEY`; see CLAUDE.md):
`cd $CLAUDE_PROJECT_DIR/tools/x4validate && uv run --python 3.13 python -c "from x4validate._nexus import search_mods; print(search_mods('<name>',5))"`
- A dependency `id` that is a Steam workshop id (`ws_<digits>`): get its title with
  `_nexus.steam_title('ws_...')`, then `search_mods(title)` to find the Nexus id → URL
  `https://www.nexusmods.com/x4foundations/mods/<id>`.
- Known: **SirNukes Mod Support APIs** = `mods/503`. Mark `optional="true"` deps as *(optional)*.
- If you can't resolve one, leave the name without a link rather than guessing.

## 3. Write `dist/NEXUS_DESCRIPTION.txt` (Nexus BBCode)
Nexus uses BBCode, not Markdown. Follow this proven structure, filled from §1 (drop sections
that don't apply):

```
[size=5]<Display Name>[/size]

<one-paragraph hook: what it does, for X4 9.x>

[size=4]The Problem[/size]        (only if the mod fixes a specific pain point)
<…>

[size=4]What this mod does[/size]
[list]
[*][b]<feature>[/b] — <short>
[/list]

[size=4]Configuration (optional)[/size]   (only if it has an options menu)
With [url=https://www.nexusmods.com/x4foundations/mods/503]SirNukes Mod Support APIs[/url] …
[list][*]…[/list]

[size=4]Installation[/size]
Extract into your X4 [b]extensions[/b] folder so the path becomes:
[code]X4 Foundations/extensions/<id>/content.xml[/code]
Or install with Vortex.

[size=4]Compatibility / Safety[/size]
[list]
[*][b]save="<true|false>"[/b] — <if false: removable any time, save continues vanilla>
[*]Patches <files it diffs> via [i]<diff>[/i]; may conflict with mods editing the same <cue/file>.
[*]Requirements: <resolved dependency links, noting optional ones>
[/list]

[size=4]Languages[/size]
<from t/ suffixes>
```

Also emit, for the upload form: a **title**, a **one-line summary**, a **version** string,
suggested **category** and **tags**, and the **requirements** list — as a short checklist the
user pastes into Nexus fields.

## 4. Generate the banner (1300×372)
Derive a title (1–2 lines), subtitle, and tagline from the mod; pick a theme colour.
```
uv run --with pillow python "$CLAUDE_PROJECT_DIR/tools/nexus-banner/make_banner.py" \
  --title "<LINE1>" [--title2 "<LINE2>"] \
  --subtitle "<one line>" --tagline "<a · b · c>" \
  [--primary "#RRGGBB"] --out "<mod>/dist/banner_1300x372.png"
```
Add `--no-motif` for non-network mods, or a second run with `--size 1280x720` for a hero image.
Then **show the user the PNG** to confirm before finalizing. (See `tools/nexus-banner/README.md`.)

## 5. Changelog & report
Extract the latest version's notes from `CHANGELOG.md` into a paste-ready Nexus changelog.
Report: files written to `dist/`, the resolved requirement links, and a manual-upload checklist
(category, tags, version, requirements, where each artifact goes). The actual upload is the
user's — Nexus has no publish API for mod pages.

Honor CLAUDE.md: confirm before overwriting `dist/`; state confidence; don't invent features
the mod doesn't have.
