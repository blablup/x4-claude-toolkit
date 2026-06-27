---
name: x4-nexus-publish
description: Prepare and validate a Nexus Mods release or update for an X4 mod — build the distributable archive, bump the version, prep the user's additional gallery images, assemble description/requirements/banner, and emit an exact step-by-step upload/update checklist. Use when the user wants to publish a new mod or update an existing one on Nexus, or add screenshots to a mod page.
allowed-tools: Read, Write, Glob, Grep, Bash
---

Get an X4 mod ready to ship on **Nexus Mods** and walk the user through the upload — including
**additional gallery images** they supply.

> **Honest scope:** Nexus has **no public publish/upload API** (the API is read-only metadata +
> downloads). This skill assembles and *validates* a complete, correct release and gives the
> exact manual steps; it does **not** automate the website (never scrape/drive the Nexus UI —
> that breaks their ToS and the toolkit's API-first rule). Everything up to the final web upload
> is automated.

**Input:** the mod directory. Ask up front: **new publish** or **update**? For an update, get the
existing mod's Nexus id/URL (and store it in `dist/.nexus-mod-id` for next time).

## 1. Validate — do not ship a broken mod
- `cd $CLAUDE_PROJECT_DIR/tools/x4validate && uv run --python 3.13 x4validate <mod>` → must be clean.
- Confirm `content.xml` `version` was bumped and `CHANGELOG.md` has an entry for it; sanity-check
  the `save` flag. If anything's off, stop and tell the user — don't proceed.

## 2. Page content (description + banner)
Ensure `dist/NEXUS_DESCRIPTION.txt` and a `dist/banner_1300x372.png` exist; if not, run the
**`x4-nexus-release`** skill first (it writes the BBCode description, resolves requirement links,
and generates the banner). For an update, diff the description against what changed.

## 3. Additional images (user-supplied gallery)
Ask the user for screenshot paths — files, a folder, or globs (the **order they give = gallery
order**). Normalize them into `dist/images/` (web-sized, metadata-stripped, numbered):
```
uv run --with pillow python "$CLAUDE_PROJECT_DIR/tools/nexus-banner/prep_images.py" \
  <their paths...> --out "<mod>/dist/images" --prefix gallery_ --max-width 1920 --max-height 1080
```
Then **show the user the numbered results** and let them reorder/drop before upload. (`--format jpg`
for photos/screens; keep `png` for crisp UI graphics. See `tools/nexus-banner/README.md`.)

## 4. Build the distributable archive
Package **only the runtime files** (the mod folder named by `id`, containing `content.xml` and the
game-path dirs like `md/ aiscripts/ ui/ t/ libraries/ assets/`) — exclude `docs/`, `dist/`,
`.git/`, `.claude/`, `.banner/`. Name it `<id>-<version>.zip` so it extracts to
`extensions/<id>/content.xml`:
```
# clean snapshot of tracked runtime files (run in the mod repo):
git archive --format=zip --prefix="<id>/" -o "dist/<id>-<version>.zip" HEAD \
  content.xml md aiscripts ui t libraries assets   # (only the dirs that exist)
```
(Or pack a CAT/DAT release with `bin/xrcat -in <mod> -out dist/<id>/ext_01` if the user prefers a
packed mod.) Confirm the archive contents before finishing.

## 5. Requirements
List each dependency as a requirement with its resolved Nexus link (from `x4-nexus-release` /
the Nexus API), marking optional ones. Don't guess a link you couldn't resolve.

## 6. Emit the upload / update checklist
Produce a precise, paste-ready checklist for the website:

**New mod** — Nexus → *Add a mod*:
1. Name + short summary; **Category** + **Tags** (suggested); **Game**: X4 Foundations.
2. **Description**: paste `dist/NEXUS_DESCRIPTION.txt` (BBCode).
3. **Requirements**: add each resolved link (mark optional).
4. **Files**: upload `dist/<id>-<version>.zip` as the **main file**; set **Version** = `<version>`.
5. **Images**: upload `dist/images/gallery_*` in numbered order; set the header/featured image.
6. Save as draft → preview → publish.

**Update** — Nexus → *Manage mod → Files / Images / Description*:
1. **Files → Add file**: upload `dist/<id>-<version>.zip`, set **Version**, paste the changelog
   for this version, mark as **main** (and optionally "update" the previous file).
2. Update the **Description** only if it changed; bump the displayed **Version**.
3. **Images**: add any new `dist/images/gallery_*`.

Report what was written to `dist/`, the archive path + size, the gallery order, and the resolved
requirement links. Honor CLAUDE.md: confirm before overwriting `dist/`, state confidence, and
never invent features or fabricate a Nexus link.
