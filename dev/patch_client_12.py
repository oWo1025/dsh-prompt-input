# -*- coding: utf-8 -*-
"""0.2.3-c：移动的安全校验（数量守恒）+ 字典 + 版本号。"""
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


# 1) 移动前后总数必须一致，否则宁可不动
sub("""        try {
          await commit(pagesNext)
          setFlash(sessionId, 'ok', t('movedCell'))""",
    """        // 防御：移动不该改变格子总数。数量对不上就中止，绝不静默丢内容。
        const countCells = (list) => list.reduce((sum, item) => sum + (item ? 1 : 0), 0)
        const before = pages.reduce((sum, item) => sum + countCells(item.cells), 0)
        const after = pagesNext.reduce((sum, item) => sum + countCells(item.cells), 0)
        if (before !== after) {
          setFlash(sessionId, 'err', t('moveFailed'))
          return
        }

        try {
          await commit(pagesNext)
          setFlash(sessionId, 'ok', t('movedCell'))""",
    "guard")

# 2) 字典
sub("""        movedCell: '已移动',
      },""",
    """        movedCell: '已移动',
        moveFailed: '这次移动会丢内容，已取消',
      },""",
    "dict-zh")

sub("""        movedCell: 'Moved',
      },""",
    """        movedCell: 'Moved',
        moveFailed: 'That move would lose a cell — cancelled',
      },""",
    "dict-en")

# 3) 版本
sub("const CLIENT_BUILD = '0.2.2+build1'", "const CLIENT_BUILD = '0.2.3+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.2'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.2'", "const VERSION = '0.2.3'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.3"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

print("ok ->", pkg["version"], "| size", len(src))
