#!/usr/bin/env python3
"""DA Paw on the site (2026-09-24): pull the app's 3D world into the dark half of the page.

  python3 tools/da-paw-web.py <app-repo> <captures-dir>

- <app-repo>: the React Native app (branch chantier/da-piece-principale).
- <captures-dir>: home.png, swipe.png, companion-room.png, 1179 × 2556, taken on the founder's iPhone
  (2026-09-24) with the status bar replaced by the simulator's clean 09:41 strip (rows 0-150, 24-row
  feather; the strip also brings the Dynamic Island the site's phone frames expect).

Outputs under assets/:
- img/app/{fr,en}/shot-{home,swipe,companion-room}.webp: 640 px wide, like the previous captures.
  The English page reuses the French captures until English ones are taken.
- img/paw/*.webp: the app's matte 3D objects (icons 192 px, the padlock cat 512 px), alpha kept,
  plus search-cat.webp: the cat looking for a photo on iCloud, the app's own loop, cropped square.
- video/paw-*.mp4 + .jpg: the app's cat loops (Seedance raw clips, pure black background), cropped
  square, 640 px, the last 250 ms blended back into the first frame so the loop has no seam. They are
  shown with mix-blend-mode: screen: black disappears into the page, the grain shows through the shadows.
- img/favicon-{16,32}.png: the app icon with rounded corners; apple-touch-icon.png, icon-512.png: the square icon.
Nothing is generated here: every pixel comes from the app or the founder's phone.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

SITE = pathlib.Path(__file__).resolve().parents[1]
FF = shutil.which('ffmpeg') or 'ffmpeg'

ICONS = ['photos', 'check', 'paw', 'clock', 'film', 'duplicates', 'lock', 'photo', 'settings']
CAPTURES = ['home', 'swipe', 'companion-room']
# name -> (raw clip in assets/da-paw/animations, square crop x, y, side) — crops measured on the union of
# non-black pixels over all 121 frames (hero x 485-947 y 130-573; celebrate x 288-992 y 94-611).
LOOPS = {
    'paw-cat': ('hero-cat-raw.mp4', 436, 72, 560),
    'paw-cat-wave': ('spot-celebrate-da-v2-raw.mp4', 280, 0, 720),
}
LOOP_FRAMES, SEAM = 120, 6


def captures(src: pathlib.Path) -> None:
    for lang in ('fr', 'en'):
        out = SITE / 'assets/img/app' / lang
        out.mkdir(parents=True, exist_ok=True)
        for name in CAPTURES:
            im = Image.open(src / f'{name}.png').convert('RGB')
            im = im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS)
            im.save(out / f'shot-{name}.webp', quality=88, method=6)
    print('captures → assets/img/app/{fr,en}/shot-{home,swipe,companion-room}.webp')


def objects(app: pathlib.Path) -> None:
    out = SITE / 'assets/img/paw'
    out.mkdir(parents=True, exist_ok=True)
    for name in ICONS:
        Image.open(app / f'assets/da-paw/icon3d-{name}.png').convert('RGBA').save(
            out / f'{name}.webp', quality=90, alpha_quality=100, method=6)
    Image.open(app / 'assets/da-paw/spot-locked.png').convert('RGBA').save(
        out / 'cat-lock.webp', quality=90, alpha_quality=100, method=6)
    print(f'objets 3D → assets/img/paw/ ({len(ICONS)} pictos + chat au cadenas)')


# La boucle du chat qui cherche la photo sur le Cloud (mission 129) : transparente, elle
# reste une image animée (pas une vidéo comme les boucles sur fond noir). Carré mesuré sur
# l'union des pixels opaques de la boucle entière, avec une marge.
SEARCH_LOOP = ('photo-search-cat-loop.webp', 195, 23, 322)


def search_loop(app: pathlib.Path) -> None:
    name, x, y, side = SEARCH_LOOP
    src = Image.open(app / 'assets/da-paw/animations' / name)
    # Une image sur deux, à 192 px : la boucle pèse alors ~300 Ko au lieu de 1,6 Mo pour un
    # picto de 136 px, et le mouvement (le chat qui inspecte) reste lisible.
    frames, durations = [], []
    for i in range(0, src.n_frames, 2):
        src.seek(i)
        f = src.convert('RGBA').crop((x, y, x + side, y + side)).resize((192, 192), Image.LANCZOS)
        frames.append(f)
        durations.append(2 * src.info.get('duration', 42))
    out = SITE / 'assets/img/paw/search-cat.webp'
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, quality=58, method=4, allow_mixed=True)
    print(f'chat qui cherche → assets/img/paw/search-cat.webp ({len(frames)} images, '
          f'{out.stat().st_size // 1024} Ko)')


def loops(app: pathlib.Path) -> None:
    out = SITE / 'assets/video'
    out.mkdir(parents=True, exist_ok=True)
    for name, (clip, x, y, side) in LOOPS.items():
        raw = subprocess.run([FF, '-v', 'error', '-i', str(app / 'assets/da-paw/animations' / clip),
                              '-vf', f'crop={side}:{side}:{x}:{y},scale=640:640:flags=lanczos',
                              '-frames:v', str(LOOP_FRAMES), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             capture_output=True, check=True).stdout
        frames = np.frombuffer(raw, np.uint8).reshape(-1, 640, 640, 3).astype(np.float32).copy()
        first = frames[0].copy()
        for i in range(LOOP_FRAMES - SEAM, LOOP_FRAMES):
            t = (i - (LOOP_FRAMES - SEAM) + 1) / SEAM
            t = t * t * (3 - 2 * t)
            frames[i] = frames[i] * (1 - t) + first * t
        enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '640x640',
                                '-r', '24', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '24',
                                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', str(out / f'{name}.mp4')],
                               stdin=subprocess.PIPE)
        enc.communicate(np.clip(frames, 0, 255).round().astype(np.uint8).tobytes())
        Image.fromarray(first.round().astype(np.uint8)).save(out / f'{name}.jpg', quality=86)
        print(f'{name}.mp4 : {(out / f"{name}.mp4").stat().st_size // 1024} Ko')


def _rounded(icon: Image.Image, size: int) -> Image.Image:
    """The icon on its black square with rounded corners, like the app on the home screen (founder, 2026-09-24:
    the browser tab keeps the black background). Continuous corners, the iOS shape: a superellipse of exponent 5
    filling the square, drawn at 8x and shrunk so its edge is smooth even at 16 px."""
    big = size * 8
    c = (np.arange(big) + 0.5) / big * 2 - 1
    mask = (np.abs(c)[None, :] ** 5 + np.abs(c)[:, None] ** 5) <= 1
    alpha = Image.fromarray((mask * 255).astype(np.uint8)).resize((size, size), Image.BOX)
    out = icon.resize((size, size), Image.LANCZOS).convert('RGBA')
    out.putalpha(alpha)
    return out


def icons(app: pathlib.Path) -> None:
    icon = Image.open(app / 'assets/icon.png').convert('RGB')
    img = SITE / 'assets/img'
    for size, name in [(16, 'favicon-16.png'), (32, 'favicon-32.png')]:
        _rounded(icon, size).save(img / name, optimize=True)
    # The home-screen icon stays square and opaque: iOS rounds it itself and fills any transparency with black.
    for size, name in [(180, 'apple-touch-icon.png'), (512, 'icon-512.png')]:
        icon.resize((size, size), Image.LANCZOS).save(img / name, optimize=True)
    print('icônes → favicon-16/32 (fond noir, coins arrondis), apple-touch-icon, icon-512')


if __name__ == '__main__':
    app, caps = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    captures(caps)
    objects(app)
    loops(app)
    search_loop(app)
    icons(app)
