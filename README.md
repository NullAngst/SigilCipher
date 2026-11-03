# Sigil Cipher

A font where every letter, digit and a few punctuation marks type as the sigil glyphs from my profile-picture seals, for anyone who wants to write NULL ANGST or anything else in the cipher.

Type normal text and it comes out as sigils. Lowercase and uppercase give the same glyph.

## What's in here

- `fonts/SigilCipher-Regular.ttf` and `fonts/SigilCipher-Bold.ttf`, the desktop fonts
- `fonts/SigilCipher-Regular.woff2` and `fonts/SigilCipher-Bold.woff2`, for web pages
- `fonts/specimen.png`, the key: every sigil with the character that types it
- `build_font.py`, the script that draws every glyph and builds the fonts

## License

Sigil Cipher is licensed under CC BY-ND 4.0. The full text is in `LICENSE`.

- You can use it anywhere, for anything, including commercial work, logos, merch and web pages.
- You can copy it and share it as-is.
- You have to credit it. "Sigil Cipher by NullAngst" with a link to the license is enough.
- You cannot share a modified version. That covers altered glyphs, added glyphs and a changed build script.

Converting it to another format, like TTF to WOFF2, doesn't count as modifying it. Using it to set type in a document or on a site doesn't either.

## Prerequisites

To just use the font, nothing. Any Linux desktop with fontconfig, which is all of them.

To rebuild it after changing a glyph:

- Python 3.9 or newer
- The `fonttools`, `shapely` (2.0 or newer), `brotli` and `pillow` Python packages

## Install the font

1. Make the user font folder: `mkdir -p ~/.local/share/fonts`
2. Copy the fonts in: `cp fonts/SigilCipher-*.ttf ~/.local/share/fonts/`
3. Refresh the font cache: `fc-cache -f`
4. Check it registered: `fc-list | grep "Sigil Cipher"`. You should see both Regular and Bold.

Apps that were already open need a restart before "Sigil Cipher" shows up in their font list.

## Use it on a web page

Copy the two `.woff2` files next to your stylesheet, then:

```css
@font-face {
  font-family: "Sigil Cipher";
  src: url("SigilCipher-Regular.woff2") format("woff2");
  font-weight: 400;
}
@font-face {
  font-family: "Sigil Cipher";
  src: url("SigilCipher-Bold.woff2") format("woff2");
  font-weight: 700;
}
.sigil { font-family: "Sigil Cipher"; }
```

## Typing the seal bands

The rings on the seals use two separators:

- `|` types the diamond that marks the start of each repeat
- `.` types the small dot between words

So `|NULL.ANGST|` and `|35.RUINS|` reproduce the ring text. A normal space is a blank gap, half a glyph wide.

## Rebuild after changing a glyph

This section is for me. Under the license, anyone else can rebuild for their own use but can't share the result.

I run Kubuntu, so in my case the system Python is locked against `pip install` and a venv is the clean way around it. Same deal on any recent Debian, Ubuntu or Fedora.

1. Make a venv: `python3 -m venv ~/.venvs/sigil`
2. Install the packages into it: `~/.venvs/sigil/bin/pip install fonttools shapely brotli pillow`
3. Edit the glyph in `build_font.py`. They're all in the `GLYPHS` table, drawn on a 14x14 grid from -7 to 7 with y pointing down.
4. Build: `~/.venvs/sigil/bin/python build_font.py fonts --specimen`
5. Open `fonts/specimen.png` and look at what you changed.
6. Reinstall with the steps under "Install the font".

The glyph tools are:

- `L(points...)`: an open line with square ends
- `F(points...)`: an open line with flat ends, for marks that stop on another stroke so they don't poke out
- `Z(points...)`: a closed outline
- `C(x, y, r)`: a circle outline
- `D(x, y, r)`: a filled dot
- `arc(x, y, r, start, end)`: part of a circle, angles in degrees, 0 is to the right and 90 is down

Stroke widths for Regular and Bold are in `WEIGHTS` near the top, if you want them heavier or lighter.
