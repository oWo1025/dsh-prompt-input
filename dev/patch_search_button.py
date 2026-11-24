# -*- coding: utf-8 -*-
"""0.3.3：隐藏 input[type=search] 的原生清除按钮（和面板的 ✕ 撞车）。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"
CLIENT = os.path.join(DEV, "client.js")
src = open(CLIENT, encoding="utf-8").read()

old = ".dsq-search::placeholder{color:var(--dsw-alias-label-secondary,#667085);opacity:.9}"
assert src.count(old) == 1
new = (
    old
    + "\n/* 关掉 Chromium 的搜索清除按钮：它会和面板自己的 ✕ 撞在一起，而且自带蓝色圆点 */"
    + "\n.dsq-search::-webkit-search-cancel-button,.dsq-search::-webkit-search-decoration{-webkit-appearance:none;appearance:none}"
)
src = src.replace(old, new)

assert src.count("const CLIENT_BUILD = '0.3.2+build1'") == 1
src = src.replace("const CLIENT_BUILD = '0.3.2+build1'", "const CLIENT_BUILD = '0.3.3+build1'")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.3.2'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.3.2'", "const VERSION = '0.3.3'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.3.3"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

CL = os.path.join(DEV, "CHANGELOG.md")
c = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
if "0.3.3 —" not in c:
    c = head + """## 0.3.3 — 隐藏搜索框的原生清除按钮

`<input type="search">` 在 Chromium 里自带一个蓝色圆点的清除按钮，和面板右上角自己的 ✕ 撞在一起。
用 `::-webkit-search-cancel-button { appearance: none }` 关掉，只留面板那个 ✕（它同时负责收起面板）。

""" + c[len(head):]
    open(CL, "w", encoding="utf-8", newline="\n").write(c)

print("ok ->", pkg["version"])
