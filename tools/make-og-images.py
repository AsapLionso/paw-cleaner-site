#!/usr/bin/env python3
"""The share images (Open Graph), French and English (2026-09-17).

  python3 tools/make-og-images.py

Run after tools/sync-app-assets.py: everything comes from the site's own assets.
Left, the sorting world (black, the wordmark, two lines in the app's pixel typeface);
right, the companion's world (parchment behind a stepped pixel edge, the kitten on the
Kibble platform, the room screenshot in a phone). Only the kitten is ever shown: the
later looks stay a surprise (founder, 2026-09-17).

Outputs: assets/img/og-image.jpg (French, the default page) and og-image-en.jpg.
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont

SITE = pathlib.Path(__file__).resolve().parents[1]
IMG = SITE / 'assets/img'
W, H = 1200, 630
EDGE_X = 752            # where the warm world begins
STEP = 8                # the stepped edge moves by 8 px, like the site's pixel edges
INK = (4, 4, 4)
PARCHMENT = (235, 224, 196)
WHITE = (237, 237, 237)
HONEY = (238, 194, 122)
GREY = (150, 150, 150)
TEXT_LEFT = 75
TEXT_RIGHT = EDGE_X - 40

LINES = {
    'fr': ('TRIE TES PHOTOS.', 'FAIS GRANDIR TON CHAT.', 'og-image.jpg', 'fr'),
    'en': ('SORT YOUR PHOTOS.', 'GROW A LITTLE CAT.', 'og-image-en.jpg', 'en'),
}


def spaced_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, tracking: int) -> int:
    return sum(draw.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1)


def draw_spaced(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill, tracking: int) -> None:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def fitted_tracking(draw: ImageDraw.ImageDraw, lines: tuple[str, ...], font: ImageFont.FreeTypeFont) -> int:
    """The widest letter spacing (at most 6 px) at which every line fits. Silkscreen stays at
    32 px, 4 px per font pixel, so both languages share one size and stay crisp."""
    for tracking in range(6, -1, -1):
        if all(spaced_width(draw, line, font, tracking) <= TEXT_RIGHT - TEXT_LEFT for line in lines):
            return tracking
    raise SystemExit('les lignes ne tiennent pas')


def make(lang: str) -> None:
    line1, line2, out_name, shot_lang = LINES[lang]
    im = Image.new('RGB', (W, H), INK)
    draw = ImageDraw.Draw(im)

    # The warm world, behind a stepped edge (one 8 px step every 8 px of height, back and forth).
    offsets = [0, 8, 16, 8, 0, 8, 0, -8, 0, 8]
    for y in range(0, H, STEP):
        x = EDGE_X + offsets[(y // STEP) % len(offsets)] - 8
        draw.rectangle((x, y, W, y + STEP - 1), fill=PARCHMENT)

    # The wordmark.
    logo = Image.open(IMG / 'logo.png').convert('RGBA')
    logo_w = 430
    logo = logo.resize((logo_w, round(logo.height * logo_w / logo.width)), Image.LANCZOS)
    im.paste(logo, (TEXT_LEFT, 172), logo)

    # Two lines in Silkscreen, the second in honey, and the address.
    bold = SITE / 'assets/fonts/silkscreen-700.ttf'
    regular = SITE / 'assets/fonts/silkscreen-400.ttf'
    font = ImageFont.truetype(str(bold), 32)
    tracking = fitted_tracking(draw, tuple(line for pair in LINES.values() for line in pair[:2]), font)
    draw_spaced(draw, (TEXT_LEFT, 308), line1, font, WHITE, tracking)
    draw_spaced(draw, (TEXT_LEFT, 308 + round(font.size * 1.55)), line2, font, HONEY, tracking)
    small = ImageFont.truetype(str(regular), 24)
    draw_spaced(draw, (TEXT_LEFT, 444), 'PAWCLEANER.APP', small, GREY, 3)

    # The phone with the room screenshot (the kitten).
    shot = Image.open(IMG / 'app' / shot_lang / 'shot-companion-room.webp').convert('RGB')
    screen_w = 250
    screen = shot.resize((screen_w, round(shot.height * screen_w / shot.width)), Image.LANCZOS)
    px, py = 912, 40
    frame = (px - 12, py - 12, px + screen_w + 12, py + screen.height + 12)
    draw.rounded_rectangle(frame, radius=44, fill=(10, 10, 10), outline=(70, 70, 70), width=2)
    mask = Image.new('L', screen.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, screen.width - 1, screen.height - 1), radius=34, fill=255)
    im.paste(screen, (px, py), mask)
    notch_w = 78
    draw.rounded_rectangle((px + (screen_w - notch_w) // 2, py + 9, px + (screen_w + notch_w) // 2, py + 31), radius=11, fill=(0, 0, 0))

    # The kitten on the Kibble platform, twice its art size.
    platform = Image.open(IMG / 'pixel/platform.png').convert('RGBA')
    plank_h = 16
    plank = platform.resize((round(platform.width * plank_h / platform.height), plank_h), Image.NEAREST)
    plank_w = 132
    plank = plank.crop((0, 0, plank_w, plank_h))
    plank_x, plank_y = 766, 470
    im.paste(plank, (plank_x, plank_y), plank)
    cat = Image.open(IMG / 'pixel/cat-1.png').convert('RGBA')
    box = cat.getchannel('A').getbbox()
    cat = cat.crop(box)
    scale = 2
    cat = cat.resize((cat.width * scale, cat.height * scale), Image.NEAREST)
    im.paste(cat, (plank_x + (plank_w - cat.width) // 2, plank_y - cat.height + 4), cat)

    out = IMG / out_name
    im.save(out, 'JPEG', quality=88, optimize=True, progressive=True)
    print(f'{out.relative_to(SITE)}  {im.size}  police {font.size} px, approche {tracking} px  {out.stat().st_size // 1024} Ko')


if __name__ == '__main__':
    for lang in LINES:
        make(lang)
