# -*- coding: utf-8 -*-
"""调整图标几何：细一点的描边、更开的行距，让 256px 下两行字能分开；同步 icon.svg。"""
import io
import os
import sys
from PIL import Image, ImageDraw

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"

# ---------------------------------------------------------------- SVG
SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="Prompt 面板">
  <g fill="none" stroke="#4d6bfe" stroke-linejoin="round">
    <g transform="rotate(-9 14.25 7.8)">
      <rect x="6.9" y="2.2" width="13.6" height="9.4" rx="2.7" stroke-width="1.7" opacity="0.42"/>
    </g>
    <rect x="2.6" y="9.7" width="14.2" height="9.8" rx="2.8" stroke-width="1.7"/>
    <path d="M5.9 13.4h6.4M5.9 16.5h3.8" stroke-width="1.5" stroke-linecap="round"/>
  </g>
</svg>
'''
open(os.path.join(DEV, "icon.svg"), "w", encoding="utf-8", newline="\n").write(SVG)

# ---------------------------------------------------------------- PNG
OUT = os.path.join(DEV, "icon-256.png")
SIZE = 256
SS = 4
PX = SIZE * SS
U = PX / 24.0
BLUE = (77, 107, 254, 255)


def card(cx, cy, w, h, r, sw, alpha=255, angle=0.0):
    layer = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
        radius=r, outline=BLUE, width=sw,
    )
    if alpha < 255:
        a = layer.getchannel("A").point(lambda v: int(v * alpha / 255))
        layer.putalpha(a)
    if angle:
        layer = layer.rotate(angle, center=(14.25 * U, 7.8 * U), resample=Image.BICUBIC)
    return layer


base = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
base = Image.alpha_composite(base, card(
    14.25 * U, 6.9 * U, 13.6 * U, 9.4 * U, 2.7 * U, max(1, round(1.7 * U)), alpha=107, angle=-9,
))
base = Image.alpha_composite(base, card(
    9.7 * U, 14.6 * U, 14.2 * U, 9.8 * U, 2.8 * U, max(1, round(1.7 * U)),
))

lines = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
d = ImageDraw.Draw(lines)
lw = max(1, round(1.5 * U))
for y, x2 in ((13.4, 12.3), (16.5, 9.7)):
    d.line([(5.9 * U, y * U), (x2 * U, y * U)], fill=BLUE, width=lw)
base = Image.alpha_composite(base, lines)

base.resize((SIZE, SIZE), Image.LANCZOS).save(OUT, optimize=True)
print("svg + png updated:", os.path.getsize(OUT), "bytes")
