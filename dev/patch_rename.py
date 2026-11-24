# -*- coding: utf-8 -*-
"""去掉从上游继承的「应声」名字：README / package.json / icon / 源码注释。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
NAME = "快捷输入"

edits = {
    "README.md": [("# 应声 · 快捷输入\n", "# 快捷输入（Quick Input）\n")],
    "client.js": [(" * 应声 · 快捷输入 —— 浏览器半区。", " * 快捷输入 —— 浏览器半区。")],
    "index.js": [(" * 应声 · 快捷输入 —— 宿主半区。", " * 快捷输入 —— 宿主半区。")],
    "cordis.patch.yml": [("# 应声 · 快捷输入的配置层。", "# 快捷输入的配置层。")],
    "icon.svg": [
        ('aria-label="应声 · 快捷输入"', 'aria-label="快捷输入"'),
    ],
}

for name, pairs in edits.items():
    path = os.path.join(DEV, name)
    text = open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert text.count(old) == 1, f"{name}: expected 1 got {text.count(old)} for {old[:40]!r}"
        text = text.replace(old, new)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("ok", name)

pkg_path = os.path.join(DEV, "package.json")
pkg = json.load(open(pkg_path, encoding="utf-8"))
assert pkg["description"].startswith("应声 · ")
pkg["description"] = pkg["description"].replace("应声 · ", "", 1)
json.dump(pkg, open(pkg_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(pkg_path, "a", encoding="utf-8").write("\n")
print("ok package.json ->", pkg["description"][:40])

left = []
for root, dirs, files in os.walk(DEV):
    if ".git" in root:
        continue
    for name in files:
        if not name.endswith((".md", ".js", ".json", ".yml", ".svg")):
            continue
        p = os.path.join(root, name)
        if "应声" in open(p, encoding="utf-8", errors="ignore").read():
            left.append(os.path.relpath(p, DEV))
print("remaining 应声:", left)
