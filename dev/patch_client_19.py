# -*- coding: utf-8 -*-
"""0.2.9：强调色改用 DSH 真正的品牌蓝 token；预览页改为真实 token 值。"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
CLIENT = os.path.join(DEV, "client.js")
src = open(CLIENT, encoding="utf-8").read()

OLD = "var(--dsw-alias-brand-primary,#4d6bfe)"
NEW = "var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))"
count = src.count(OLD)
assert count >= 10, count
src = src.replace(OLD, NEW)
print("accent token replaced:", count, "occurrences")

assert src.count("const CLIENT_BUILD = '0.2.8+build1'") == 1
src = src.replace("const CLIENT_BUILD = '0.2.8+build1'", "const CLIENT_BUILD = '0.2.9+build1'")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.8'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.8'", "const VERSION = '0.2.9'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.9"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

# ---------------------------------------------------------------- 预览：用真实 token
PREV = os.path.join(DEV, "dev", "preview.py")
pv = open(PREV, encoding="utf-8").read()
pairs = [
    ("  --dsw-alias-brand-primary:#4d6bfe;",
     "  --dsw-alias-brand-primary:#1a1d21;          /* 浅色主题下这是近黑 */\n  --dsw-alias-brand-primary-new-color:#4176e6; /* 真正的品牌蓝 */"),
    ("  --dsw-alias-border-selected:#4d6bfe;",
     "  --dsw-alias-border-selected:#9aa3b2;"),
]
for old, new in pairs:
    assert pv.count(old) == 1, f"preview token missing: {old[:30]!r}"
    pv = pv.replace(old, new)
open(PREV, "w", encoding="utf-8", newline="\n").write(pv)
print("preview tokens -> real DSH values")

print("ok ->", pkg["version"], "| size", len(src))
