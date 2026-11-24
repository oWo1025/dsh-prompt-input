# -*- coding: utf-8 -*-
"""0.2.7：入口图标定为「后卡微旋的一叠卡」（避开"复制"语义）。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
CLIENT = os.path.join(DEV, "client.js")
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    got = src.count(old)
    assert got == 1, f"[{label}] expected 1 got {got}"
    src = src.replace(old, new)


OLD_ICON = """      return h(
        'svg',
        { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', stroke: 'currentColor', 'aria-hidden': 'true' },
        h('rect', {
          x: 4.9,
          y: 1.6,
          width: 9.5,
          height: 6.6,
          rx: 1.9,
          strokeWidth: 1.3,
          opacity: 0.45,
        }),
        h('rect', { x: 1.6, y: 6.3, width: 9.5, height: 6.6, rx: 1.9, strokeWidth: 1.3 }),
        h('path', {
          d: 'M3.9 9.1h4.4M3.9 11.2h2.8',
          strokeWidth: 1.2,
          strokeLinecap: 'round',
        }),
      )"""

NEW_ICON = """      return h(
        'svg',
        { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', stroke: 'currentColor', 'aria-hidden': 'true' },
        // 后面那张微微歪着：两卡等大会被读成"复制"，歪一点才是"一叠"。
        h(
          'g',
          { transform: 'rotate(-9 9.5 5.2)' },
          h('rect', {
            x: 4.6,
            y: 1.4,
            width: 9.2,
            height: 6.4,
            rx: 1.8,
            strokeWidth: 1.3,
            opacity: 0.42,
          }),
        ),
        h('rect', { x: 1.7, y: 6.4, width: 9.5, height: 6.6, rx: 1.9, strokeWidth: 1.3 }),
        h('path', {
          d: 'M4 9.2h4.4M4 11.3h2.8',
          strokeWidth: 1.2,
          strokeLinecap: 'round',
        }),
      )"""

sub(OLD_ICON, NEW_ICON, "grid-icon")

sub("const CLIENT_BUILD = '0.2.6+build1'", "const CLIENT_BUILD = '0.2.7+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.6'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.6'", "const VERSION = '0.2.7'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.7"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

ICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="快捷输入">
  <g fill="none" stroke="#4d6bfe" stroke-linejoin="round">
    <g transform="rotate(-9 14.25 7.8)">
      <rect x="6.9" y="2.1" width="13.8" height="9.6" rx="2.7" stroke-width="1.95" opacity="0.42"/>
    </g>
    <rect x="2.55" y="9.6" width="14.25" height="9.9" rx="2.85" stroke-width="1.95"/>
    <path d="M6 13.8h6.6M6 16.95h4.2" stroke-width="1.8" stroke-linecap="round"/>
  </g>
</svg>
'''
open(os.path.join(DEV, "icon.svg"), "w", encoding="utf-8", newline="\n").write(ICON)

print("ok ->", pkg["version"], "| size", len(src))
