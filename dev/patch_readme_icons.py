# -*- coding: utf-8 -*-
"""图标叫法同步：README（中/英）、空状态文案、预览页。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"

README = os.path.join(DEV, "README.md")
s = open(README, encoding="utf-8").read()
pairs = [
    ("点 ⊞ 打开气泡", "点叠卡图标打开气泡"),
    ("装好后输入框工具行最左边出现 **⊞**。", "装好后输入框工具行最左边出现**叠卡图标**（两张叠起的卡片）。"),
    ("| 点 ⊞ |", "| 点叠卡图标 |"),
    ("| 再点 ⊞ /", "| 再点一次图标 /"),
    ("（点 ⊞ 自己不算", "（点图标自己不算"),
    ("点底部的 `✎` 进入编辑态：", "点底部的铅笔按钮进入编辑态："),
    ("click **⊞** next to the input box,", "click the **stack icon** next to the input box,"),
]
for old, new in pairs:
    assert s.count(old) == 1, f"README missing {old[:30]!r} ({s.count(old)})"
    s = s.replace(old, new)
open(README, "w", encoding="utf-8", newline="\n").write(s)
print("README ok; remaining ⊞:", s.count("⊞"), "✎:", s.count("✎"))

CLIENT = os.path.join(DEV, "client.js")
c = open(CLIENT, encoding="utf-8").read()
old = "emptyPageHint: '点底部的 ✎ 添加第一条',"
new = "emptyPageHint: '点底部的铅笔按钮添加第一条',"
assert c.count(old) == 1
c = c.replace(old, new)
old_en = "emptyPageHint: 'Click ✎ at the bottom to add one',"
new_en = "emptyPageHint: 'Click the pencil button at the bottom to add one',"
assert c.count(old_en) == 1
c = c.replace(old_en, new_en)
open(CLIENT, "w", encoding="utf-8", newline="\n").write(c)
print("client dict ok")

PREV = os.path.join(DEV, "dev", "preview.py")
p = open(PREV, encoding="utf-8").read()
p = p.replace("点底部的 ✎ 添加第一条", "点底部的铅笔按钮添加第一条")
open(PREV, "w", encoding="utf-8", newline="\n").write(p)
print("preview ok")

# 包描述里也别再提 ⊞
PKG = os.path.join(DEV, "package.json")
pkg = json.load(open(PKG, encoding="utf-8"))
if "⊞" in pkg["description"]:
    pkg["description"] = pkg["description"].replace("点开输入框左侧的 ⊞", "点开输入框左侧的叠卡图标")
    json.dump(pkg, open(PKG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    open(PKG, "a", encoding="utf-8").write("\n")
print("desc:", pkg["description"][:60])
