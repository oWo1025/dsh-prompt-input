# -*- coding: utf-8 -*-
"""把 README 与市场条目里的截图引用换成新的英文编号文件名。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"
RAW = "https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/docs/"

# ---------------------------------------------------------------- README
P = os.path.join(DEV, "README.md")
s = open(P, encoding="utf-8").read()
old = "![界面](docs/panel.png)"
assert s.count(old) == 1
new = """![主面板](docs/01-main.png)

<details>
<summary>更多界面：搜索、单格编辑器、编辑态、空页</summary>

| 搜索 | 单格编辑器 |
|---|---|
| ![搜索](docs/03-search.png) | ![编辑器](docs/02-edit-cell.png) |

| 编辑态（拖动排序） | 空页 |
|---|---|
| ![编辑态](docs/04-edit-grid.png) | ![空页](docs/05-empty-page.png) |

</details>"""
s = s.replace(old, new)
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("README image block replaced")

# ---------------------------------------------------------------- RELEASE.md
R = os.path.join(DEV, "docs", "RELEASE.md")
r = open(R, encoding="utf-8").read()
old_block = '''  "icon": "https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/icon.svg",
  "screenshots": [
    "https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/docs/panel.png"
  ]'''
assert r.count(old_block) == 1, r.count(old_block)
new_block = '''  "icon": "https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/icon.svg",
  "screenshots": [
    "%s01-main.png",
    "%s03-search.png",
    "%s04-edit-grid.png",
    "%s02-edit-cell.png",
    "%s05-empty-page.png"
  ]''' % (RAW, RAW, RAW, RAW, RAW)
r = r.replace(old_block, new_block)
open(R, "w", encoding="utf-8", newline="\n").write(r)
print("RELEASE.md screenshots updated")

print("\nscreenshots 顺序:")
for line in new_block.splitlines():
    if ".png" in line:
        print("  ", line.strip())
