#!/usr/bin/env python3
"""Pull the app's real visuals into the site (build 9, updated 2026-09-17).

Nothing on the page is redrawn for the web: every pixel sprite, shop item and
screenshot comes from the Paw Cleaner app itself.

  python3 tools/sync-app-assets.py <app-repo> [<captures-fr> <captures-en>]

Sans les deux dossiers de captures, tout est refait sauf les captures d'écran.

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
    # Les crocks « Éclats précieux » et les chats de l'Atelier enchanté (2026-09-25) : peints,
    # jamais sur grille. Deux fois leur taille d'affichage (32 px pour un crock, 192 pour un chat).
    'crock-common': 96, 'crock-rare': 96, 'crock-epic': 96, 'crock-legendary': 96,
    'cat-1': 384, 'cat-2-shadow': 384, 'cat-3-shadow': 384, 'cat-4-shadow': 384,
    'cat-5-shadow': 384, 'cat-6-shadow': 384,
}

# Les six allures du familier, dans l'ordre du jeu (jours 0, 7, 15, 30, 90, 180), telles que
# tools/image-bench/atelier-cats.py les écrit dans assets/companion/atelier/<robe>/.
CAT_STAGES = ('kitten', 'young', 'adult', 'bonded', 'guardian', 'legend')
CAT_COAT = 'charcoal'   # la robe historique, celle de tous les anciens profils
# Les six robes, dans l'ordre de l'écran de choix de l'app (src/companion/catVariants.ts).
CAT_COATS = ('charcoal', 'cream', 'ginger', 'siamese', 'silver_tabby', 'tuxedo')

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


WARM_INK = (36, 57, 44)     # --warm-ink du site


def silhouette(src: pathlib.Path, dst: pathlib.Path, max_side: int) -> tuple[str, tuple[int, int]]:
    """La forme seule, remplie à plat : on ne garde que l'alpha du fichier de l'app."""
    alpha = Image.open(src).convert('RGBA').getchannel('A')
    if max(alpha.size) > max_side:
        r = max_side / max(alpha.size)
        alpha = alpha.resize((max(1, round(alpha.width * r)), max(1, round(alpha.height * r))), Image.LANCZOS)
    im = Image.new('RGBA', alpha.size, WARM_INK + (0,))
    im.putalpha(alpha)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, optimize=True)
    return f'{dst.relative_to(SITE)}  {im.size} silhouette', im.size

def main() -> None:
    if len(sys.argv) not in (2, 4):
        raise SystemExit(__doc__)
    app = pathlib.Path(sys.argv[1]).resolve()
    # Sans dossiers de captures : tout sauf les captures d'écran (sprites, boutique, police).
    # Les captures demandent un appareil ; les sprites, non.
    captures = (
        {'fr': pathlib.Path(sys.argv[2]).resolve(), 'en': pathlib.Path(sys.argv[3]).resolve()}
        if len(sys.argv) == 4 else {}
    )
    warm = app / 'assets/companion/room-warm'
    atelier = app / 'assets/companion/atelier' / CAT_COAT
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

    # ── The cat (Atelier enchanté, 2026-09-25): the first look, then silhouettes for the five
    # others (founder: never spoil a later look). Painted art, no blink frame exists any more. ──
    # Jamais recadré : les six allures partagent un canevas de 576 px, pattes à la même hauteur —
    # le recadrer casserait l'échelle et l'alignement de la frise.
    report.append(sprite(atelier / f'{CAT_STAGES[0]}-normal.png', out_img / 'pixel' / 'cat-1.png',
                         PAINTED_MAX_SIDE['cat-1'])[0])
    for n, stage in enumerate(CAT_STAGES[1:], start=2):
        # La silhouette de l'app ne porte QUE sa forme : son alpha est exact, mais ses pixels sont
        # ceux de la planche (une trame à deux tons), que l'app recouvre d'une teinte. Le web n'en
        # a pas : on remplit la forme à plat, à l'encre du monde chaud (--warm-ink).
        report.append(silhouette(atelier / f'{stage}-silhouette.png', out_img / 'pixel' / f'cat-{n}-shadow.png',
                                 PAINTED_MAX_SIDE[f'cat-{n}-shadow'])[0])

    # ── Les six robes, à l'allure du jour 0 seulement (jamais une allure plus tardive) ──
    for coat in CAT_COATS:
        report.append(sprite(app / 'assets/companion/atelier' / coat / f'{CAT_STAGES[0]}-normal.png',
                             out_img / 'pixel' / f'coat-{coat.replace("_", "-")}.png',
                             PAINTED_MAX_SIDE['cat-1'])[0])

    # ── The crocks « Éclats précieux » (2026-09-25): one folder of their own in the app ──
    for rarity in ('common', 'rare', 'epic', 'legendary'):
        report.append(sprite(app / 'assets/companion/crocks' / f'{rarity}.png',
                             out_img / 'pixel' / f'crock-{rarity}.png',
                             PAINTED_MAX_SIDE[f'crock-{rarity}'], trim=True)[0])

    # ── Warm UI sprites: chests, crocks, diamond, room icons, game pieces ──
    for name, file in {
        'chest-closed': 'warm_chest_closed.png',
        'chest-ajar': 'warm_chest_ajar.png',
        'chest-open': 'warm_chest_open.png',
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
        'card-back': 'warm_memory_card_back.png',
        'snow-globe': 'warm_decor_snow_globe.png',
        'bobber': 'warm_fishing_bobber.png',
        'fish-1': 'warm_fishing_fish_1.png',
        'fish-2': 'warm_fishing_fish_2.png',
        'reed-1': 'warm_fishing_reed_1.png',
        'reed-2': 'warm_fishing_reed_2.png',
    }.items():
        report.append(sprite(warm / file, out_img / 'pixel' / f'{name}.png', PAINTED_MAX_SIDE.get(name))[0])

    # ── Croquettes : le monde du JOUR 0 (le jardin), celui que voit un nouveau joueur.
    # Depuis les missions 123-124, le jeu a six mondes et fait tomber les crocks Éclats
    # précieux : l'ancien ciel sans étoiles, sa lune, ses nuages et ses croquettes n'existent
    # plus dans l'app. Le décor est cadré sur sa moitié basse (la maison et les fleurs) ;
    # la plateforme est la bande pleine de la planche (platformTop/platformHeight du code). ──
    garden = Image.open(app / 'assets/minigame/evolutions/j0-jardin-background.png').convert('RGB')
    report.append(webp(garden.crop((0, garden.height - 470, garden.width, garden.height)),
                       out_img / 'pixel' / 'scene-garden.webp', 82))
    plank = Image.open(app / 'assets/minigame/evolutions/j0-jardin-platform.png').convert('RGBA')
    plank = plank.crop((0, 228, plank.width, 228 + 120))
    plank = plank.resize((640, round(plank.height * 640 / plank.width)), Image.LANCZOS)
    plank.save(out_img / 'pixel' / 'platform.png', optimize=True)
    report.append(f'assets/img/pixel/platform.png  {plank.size} plateforme du jardin')
    report.append(sprite(app / 'assets/minigame/evolutions/drop-bomb.png',
                         out_img / 'pixel' / 'bomb.png', 128, trim=True)[0])

    # ── Painted scene backgrounds (not on a grid): cropped to what the cards show ──
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
