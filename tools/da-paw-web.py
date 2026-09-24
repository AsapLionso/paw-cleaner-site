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
- img/paw/*.webp: the app's matte 3D objects (icons 192 px, the padlock cat 512 px), alpha kept.
- video/paw-*.mp4 + .jpg: the app's cat loops (Seedance raw clips, pure black background), cropped
  square, 640 px, the last 250 ms blended back into the first frame so the loop has no seam. They are
  shown with mix-blend-mode: screen: black disappears into the page, the grain shows through the shadows.
- img/favicon-{16,32}.png: the app icon's cat without its black square; apple-touch-icon.png, icon-512.png: the icon.
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


def _cat_cutout(icon: Image.Image) -> Image.Image:
    """The icon's cat without its black square (founder, 2026-09-24: the browser tab shows it on its own).
    The background is pure black (0), so the cat is the largest shape above it. The icon's framing cuts the body
    at the bottom edge: that edge is closed before filling holes, so the black phone held between the paws stays
    part of the cat, and the cut body fades out over the last 16 % instead of ending on a straight line. The
    square is then tightened around the cat so it reads at 16 px."""
    from scipy import ndimage

    rgb = np.asarray(icon).astype(np.float64)
    mask = rgb.max(axis=2) > 8
    lab, n = ndimage.label(mask)
    mask = lab == (np.argmax(ndimage.sum(mask, lab, range(1, n + 1))) + 1)
    h, w = mask.shape
    mask = ndimage.binary_fill_holes(np.vstack([mask, np.ones((1, w), bool)]))[:-1]
    t = np.clip((np.arange(h) / (h - 1) - 0.84) / 0.16, 0, 1)
    alpha = mask * (1 - t * t * (3 - 2 * t))[:, None]
    ys, xs = np.where(alpha > 0.02)
    side = int(max(xs.max() + 1 - xs.min(), ys.max() + 1 - ys.min()) * 1.02)
    left = int(round((xs.min() + xs.max() + 1 - side) / 2))
    top = ys.max() + 1 - side + int(side * 0.01)
    cat = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    cat.paste(Image.fromarray(np.dstack([rgb, alpha * 255]).round().clip(0, 255).astype(np.uint8)), (-left, -top))
    return cat


def icons(app: pathlib.Path) -> None:
    icon = Image.open(app / 'assets/icon.png').convert('RGB')
    img = SITE / 'assets/img'
    cat = _cat_cutout(icon).convert('RGBa')           # premultiplied, so the edges shrink without a dark fringe
    for size, name in [(16, 'favicon-16.png'), (32, 'favicon-32.png')]:
        cat.resize((size, size), Image.LANCZOS).convert('RGBA').save(img / name, optimize=True)
    # The home-screen icon stays opaque: iOS fills any transparency with black anyway.
    for size, name in [(180, 'apple-touch-icon.png'), (512, 'icon-512.png')]:
        icon.resize((size, size), Image.LANCZOS).save(img / name, optimize=True)
    print('icônes → favicon-16/32 (chat détouré), apple-touch-icon, icon-512')


if __name__ == '__main__':
    app, caps = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    captures(caps)
    objects(app)
    loops(app)
    icons(app)
