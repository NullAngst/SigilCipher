# Maintenance

A font file doesn't rot. Once it's built and installed, it keeps working. What can break is the build script, when one of its Python packages changes its API. So the check every couple of months is mostly "does it still build, and does it still look the same."

## Every couple of months

1. Update the build packages: `~/.venvs/sigil/bin/pip install --upgrade fonttools shapely brotli pillow`
2. Rebuild into a scratch folder so the working fonts stay untouched: `~/.venvs/sigil/bin/python build_font.py /tmp/sigil-check --specimen`
3. If it errors, see "When the build breaks" below. Don't overwrite `fonts/` until it builds clean.
4. Open `/tmp/sigil-check/specimen.png` next to `fonts/specimen.png` and compare them. Every glyph should look identical. Watch the line ends and the corners, since that's where a geometry library change would show first.
5. If they match, nothing else needs doing. If you changed nothing, you don't need to replace the installed fonts.
6. Delete the scratch folder: `rm -r /tmp/sigil-check`

## When the build breaks

- **shapely**: the script uses `buffer()` with `cap_style` and `join_style` given as strings (`"square"`, `"flat"`, `"mitre"`). That needs shapely 2.0 or newer. If a future release renames these, the shapely changelog will say what to use.
- **fontTools**: the script uses `FontBuilder`, `TTGlyphPen` and `timestampNow`. These have been stable for years. If one moves, the fontTools changelog will have it.
- **pillow**: only the specimen image uses it. If that breaks, build without `--specimen` and the fonts still come out fine.
- **brotli**: only the `.woff2` files need it. If it's missing, the script says so and skips them.

## After any glyph change

1. Rebuild with `--specimen` and check the image.
2. Reinstall: copy the new `.ttf` files to `~/.local/share/fonts/` and run `fc-cache -f`.
3. Bump `VERSION` in `build_font.py`.
4. Add an entry to `changes.md`.
