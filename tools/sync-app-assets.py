#!/usr/bin/env python3
"""Pull the app's real visuals into the site (build 9, updated 2026-09-17).

Nothing on the page is redrawn for the web: every pixel sprite, shop item and
screenshot comes from the Paw Cleaner app itself.

  python3 tools/sync-app-assets.py <app-repo> <captures-fr> <captures-en>

- <app-repo>: the React Native app (branch chantier/da-piece-principale).
- <captures-fr>, <captures-en>: iPhone 16 simulator captures (1179 × 2556), status bar
  overridden to 9:41, demo state with the companion under 7 days old (the kitten: the
  site never shows a later look). Four files in each: room.png, swipe.png, kibble.png,
  shop_furniture.png.

Outputs under assets/:
- img/app/{fr,en}/shot-*.webp: screenshots, 640 px wide;
- img/pixel/*.png: sprites brought back to their art resolution when they sit on an
  exact pixel grid (the cat: 6 px per art pixel), so the browser scales them crisply
  with `image-rendering: pixelated` for a few kilobytes. The cat: the first look and its
  blink frame, and only SILHOUETTES of the five later looks (founder, 2026-09-17: « ne pas
  spoil les différentes évolutions »);
- img/pixel/scene-*.webp: the painted game backgrounds (not grid-aligned);
- img/shop/*.png: the shop items shown on the page (SHOWCASE below);
- fonts/silkscreen-*.ttf + OFL.txt: the app's pixel typeface (SIL Open Font License).

It also prints the shop counts read from the app's code, and the <li> markup of the
shop grid in French and English, to paste into index.html and en/index.html.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys
from collections import Counter

import numpy as np
from PIL import Image

SITE = pathlib.Path(__file__).resolve().parents[1]


def exact_grid(im: Image.Image) -> int:
    """The largest pixel-art grid (6, 4, 3, 2) the sprite sits on exactly, else 1."""
    a = np.asarray(im.convert('RGBA')).astype(int)
    for k in (6, 4, 3, 2):
        if im.width % k or im.height % k:
            continue
        small = im.convert('RGBA').resize((im.width // k, im.height // k), Image.NEAREST)
        back = np.asarray(small.resize(im.size, Image.NEAREST)).astype(int)
        if (np.abs(a - back).max(axis=2) > 8).mean() == 0:
            return k
    return 1


def sprite(src: pathlib.Path, dst: pathlib.Path, max_side: int | None = None, trim: bool = False) -> tuple[str, int, tuple[int, int]]:
    """A sprite at its art resolution when it sits on a grid; otherwise (painted sprites
    such as the room icons or the reeds) shrunk to `max_side`, twice its largest display
    size on the page, so a 150 KB file does not ship for a 48 px icon. `trim` crops the
    transparent margin first (shop items are centred in their tile by CSS)."""
    im = Image.open(src).convert('RGBA')
    k = exact_grid(im)
    if k > 1:
        im = im.resize((im.width // k, im.height // k), Image.NEAREST)
    elif max_side and max(im.size) > max_side:
        r = max_side / max(im.size)
        im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
    if trim:
        box = im.getchannel('A').getbbox()
        if box:
            im = im.crop(box)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, optimize=True)
    return f'{dst.relative_to(SITE)}  {im.size} grid {k}', k, im.size


def webp(im: Image.Image, dst: pathlib.Path, quality: int = 82) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, 'WEBP', quality=quality, method=6)
    return f'{dst.relative_to(SITE)}  {im.size} {dst.stat().st_size // 1024} KB'


# Twice the largest size each painted (off-grid) sprite is displayed at on the page.
PAINTED_MAX_SIDE = {
    'icon-game': 112, 'icon-quests': 112, 'icon-shop': 112, 'icon-kitchen': 112, 'icon-outside': 112,
    'icon-evolution': 112, 'moon': 96, 'cloud-1': 160, 'kibble-1': 64, 'kibble-3': 64, 'card-back': 160,
    'bobber': 64, 'reed-1': 160, 'reed-2': 160, 'platform': 512,
}

# The shop items the page shows, in page order: cat things first, then a room, a kitchen,
# pieces of every rarity. Painted items are capped at 2× their largest tile size (96 px).
SHOWCASE = [
    'catTree', 'armchairWing', 'basketCatCave', 'lampPaperMoon', 'bookshelf', 'plantMapleBonsai',
    'turntable', 'bedTeepeeCat', 'fountainStone', 'chairEggShell', 'artSunburstMirror', 'woolBall',
    'lampLava', 'fridgeFifties', 'terrarium', 'screenByobu', 'crystals', 'scratchPost',
    'stove', 'landscapeFrame', 'espressoMachine', 'lanternBrass', 'bedSunPatch', 'teapot',
]
SHOP_ITEM_MAX_SIDE = 192


def kebab(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()


def shop_catalogue(app: pathlib.Path) -> tuple[list[dict], dict[str, str]]:
    """What the shop lists, read from the app's code: SHOP_ITEMS minus UNLISTED_ITEMS, with
    each item's French and English name and its warm sprite."""
    shop = (app / 'src/companion/shop.ts').read_text()
    block = shop[shop.index('export const SHOP_ITEMS'):shop.index('export const DEFAULT_OWNED')]
    items = [
        {'id': m[0], 'category': m[1], 'scene': m[2],
         'cost': {k: int(v) for k, v in re.findall(r'(\w+): (\d+)', m[3])}}
        for m in re.findall(r"\{\s*id: '(\w+)',\s*category: '(\w+)',\s*theme: '\w+',\s*scene: '(\w+)',\s*cost: \{([^}]*)\}", block)
    ]
    unlisted_block = shop[shop.index('export const UNLISTED_ITEMS'):]
    unlisted = set(re.findall(r"'(\w+)'", unlisted_block[:unlisted_block.index(']);')]))
    listed = [item for item in items if item['id'] not in unlisted]

    keys = dict(re.findall(r"^\s+(\w+): 'companion\.(item\w+)',", (app / 'src/components/ShopPanel.tsx').read_text(), re.M))

    def strings(path: str) -> dict[str, str]:
        text = (app / path).read_text()
        return {k: a or b for k, a, b in re.findall(r"^\s+(item\w+): (?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\")", text, re.M)}

    fr, en = strings('src/i18n/locales/fr.ts'), strings('src/i18n/locales/en.ts')
    sprites: dict[str, str] = {}
    for f in ('src/companion/roomThemeAssets.ts', 'src/companion/warmDecorSpritesGenerated.ts'):
        sprites.update(re.findall(r"^\s+(\w+): require\('\.\./\.\./assets/companion/room-warm/([\w.-]+\.png)'\)", (app / f).read_text(), re.M))
    for item in listed:
        key = keys.get(item['id'])
        item['fr'], item['en'], item['sprite'] = fr.get(key), en.get(key), sprites.get(item['id'])
    return listed, sprites


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    app = pathlib.Path(sys.argv[1]).resolve()
    captures = {'fr': pathlib.Path(sys.argv[2]).resolve(), 'en': pathlib.Path(sys.argv[3]).resolve()}
    warm = app / 'assets/companion/room-warm'
    sprites = app / 'assets/companion/sprites'
    out_img = SITE / 'assets/img'
    report: list[str] = []

    # ── Screenshots, per language ───────────────────────────────────────
    for lang, folder in captures.items():
        for name, file in {
            'shot-companion-room': 'room.png',
            'shot-swipe': 'swipe.png',
            'shot-kibble': 'kibble.png',
            'shot-shop': 'shop_furniture.png',
        }.items():
            im = Image.open(folder / file).convert('RGB')
            im = im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS)
            report.append(webp(im, out_img / 'app' / lang / f'{name}.webp'))

    # ── The cat: the first look and its blink; silhouettes for the five others ──
    report.append(sprite(sprites / 'cat_stage_1.png', out_img / 'pixel' / 'cat-1.png')[0])
    report.append(sprite(sprites / 'cat_stage_1_blink.png', out_img / 'pixel' / 'cat-1-blink.png')[0])
    for n in range(2, 7):
        report.append(sprite(sprites / f'cat_stage_{n}_shadow.png', out_img / 'pixel' / f'cat-{n}-shadow.png')[0])

    # ── Warm UI sprites: chests, crocks, diamond, room icons, game pieces ──
    for name, file in {
        'chest-closed': 'warm_chest_closed.png',
        'chest-ajar': 'warm_chest_ajar.png',
        'chest-open': 'warm_chest_open.png',
        'crock-common': 'warm_crock_common.png',
        'crock-rare': 'warm_crock_rare.png',
        'crock-epic': 'warm_crock_epic.png',
        'crock-legendary': 'warm_crock_legendary.png',
        'diamond': 'warm_icon_diamond.png',
        'icon-dice': 'warm_icon_dice.png',
        'icon-fishing': 'warm_icon_game_fishing.png',
        'icon-game': 'warm_icon_game.png',
        'icon-photo': 'warm_icon_photo.png',
        'icon-quests': 'warm_icon_quests.png',
        'icon-shop': 'warm_icon_shop.png',
        'icon-kitchen': 'warm_icon_kitchen.png',
        'icon-outside': 'warm_icon_outside.png',
        'icon-evolution': 'warm_icon_evolution.png',
        'moon': 'warm_minigame_moon.png',
        'cloud-1': 'warm_minigame_cloud_1.png',
        'cloud-3': 'warm_minigame_cloud_3.png',
        'kibble-1': 'warm_minigame_kibble_1.png',
        'kibble-3': 'warm_minigame_kibble_3.png',
        'bomb': 'warm_minigame_bomb.png',
        'coin': 'warm_icon_crocks.png',
        'platform': 'warm_minigame_platform.png',
        'card-back': 'warm_memory_card_back.png',
        'snow-globe': 'warm_decor_snow_globe.png',
        'bobber': 'warm_fishing_bobber.png',
        'fish-1': 'warm_fishing_fish_1.png',
        'fish-2': 'warm_fishing_fish_2.png',
        'reed-1': 'warm_fishing_reed_1.png',
        'reed-2': 'warm_fishing_reed_2.png',
    }.items():
        report.append(sprite(warm / file, out_img / 'pixel' / f'{name}.png', PAINTED_MAX_SIDE.get(name))[0])

    # ── Painted scene backgrounds (not on a grid): cropped to what the cards show ──
    sky = Image.open(warm / 'warm_minigame_sky.png').convert('RGB')
    report.append(webp(sky.crop((0, 0, 768, 512)), out_img / 'pixel' / 'scene-sky.webp', 80))
    report.append(webp(Image.open(warm / 'warm_game_fishing_bg.png').convert('RGB'), out_img / 'pixel' / 'scene-lake.webp', 80))
    floor = Image.open(warm / 'warm_floor_band.png').convert('RGB')
    report.append(webp(floor, out_img / 'pixel' / 'floor-band.webp', 85))

    # ── The shop: counts from the code, and the items the page shows ────
    listed, _ = shop_catalogue(app)
    surfaces = [item for item in listed if item['category'] in ('wall', 'floor')]
    free = [item['id'] for item in listed if not any(item['cost'].values())]
    by_id = {item['id']: item for item in listed}
    markup: dict[str, list[str]] = {'fr': [], 'en': []}
    for item_id in SHOWCASE:
        item = by_id.get(item_id)
        if not item or not (item['fr'] and item['en'] and item['sprite']):
            raise SystemExit(f'{item_id}: absent de la boutique, ou sans nom ou sans sprite chaud')
        dst = out_img / 'shop' / f'{kebab(item_id)}.png'
        line, grid, size = sprite(warm / item['sprite'], dst, SHOP_ITEM_MAX_SIDE, trim=True)
        report.append(line)
        crisp = ' class="px"' if grid > 1 else ''
        src = f'/assets/img/shop/{dst.name}'
        for lang in ('fr', 'en'):
            markup[lang].append(
                f'<li class="shop-item"><span class="shop-item__tile"><img{crisp} src="{src}" alt="" '
                f'width="{size[0]}" height="{size[1]}" loading="lazy"></span>'
                f'<span class="shop-item__name">{item[lang]}</span></li>'
            )

    # ── The pixel typeface ──────────────────────────────────────────────
    fonts = app / 'node_modules/@expo-google-fonts/silkscreen'
    (SITE / 'assets/fonts').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fonts / '400Regular/Silkscreen_400Regular.ttf', SITE / 'assets/fonts/silkscreen-400.ttf')
    shutil.copyfile(fonts / '700Bold/Silkscreen_700Bold.ttf', SITE / 'assets/fonts/silkscreen-700.ttf')
    shutil.copyfile(fonts / 'LICENSE_FONT', SITE / 'assets/fonts/OFL-silkscreen.txt')
    report.append('assets/fonts/silkscreen-400.ttf, silkscreen-700.ttf, OFL-silkscreen.txt')

    print('\n'.join(report))
    print()
    print(f'Boutique : {len(listed)} articles proposés '
          f'({dict(Counter(item["scene"] for item in listed))}), dont {len(surfaces)} murs et sols, '
          f'{len(listed) - len(surfaces)} objets à poser, {len(free)} offerts ({", ".join(free)}).')
    for lang in ('fr', 'en'):
        print(f'\n<!-- grille de la boutique ({lang}) -->')
        print('\n'.join(markup[lang]))


if __name__ == '__main__':
    main()
