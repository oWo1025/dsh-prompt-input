# -*- coding: utf-8 -*-
"""清理过时信息：package.json 描述、client.js 头注释与文案、新增 screenshots.json。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"


def edit(name, pairs):
    path = os.path.join(DEV, name)
    text = open(path, encoding="utf-8").read()
    for old, new, expect in pairs:
        got = text.count(old)
        assert got == expect, f"{name}: {old[:50]!r} expected {expect} got {got}"
        text = text.replace(old, new)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("ok", name)


# ---------------------------------------------------------------- client.js
edit("client.js", [
    # 头注释：描述当前实现
    (" * 快捷输入 —— 浏览器半区。",
     " * Prompt 面板（dsh-prompt-input）—— 浏览器半区。", 1),
    (""" * 它做三件事：
 *   - 在输入框工具行最左边画一个 ⊞（槽位 conversation.input.left）
 *   - 点开后，在输入框左上角浮出 3×3 九宫格（槽位 conversation.input.overlay）
 *   - 点某一格 → 把该格文字插到草稿的「光标处」（官方 inputActions.insertText）""",
     """ * 它做三件事：
 *   - 在输入框工具行最左边画一个叠卡图标（槽位 conversation.input.left）
 *   - 点开后在它右侧浮出气泡：搜索框 + 卡片 + 页签 + 编辑态（槽位 shell.overlay）
 *   - 点某张卡 → 把该卡文字插到草稿的「光标处」（官方 inputActions.insertText）""", 1),
    # 文案：不能再说"常驻在输入框左边"
    ("toggleShow: '展开快捷输入（常驻在输入框左边）',", "toggleShow: '展开 Prompt 面板',", 1),
    ("toggleHide: '收起快捷输入',", "toggleHide: '收起 Prompt 面板',", 1),
    ("toggleAria: '快捷输入',", "toggleAria: 'Prompt 面板',", 1),
    ("panelAria: '快捷输入九宫格',", "panelAria: 'Prompt 面板',", 1),
    ("collapse: '收起（也可点 ⊞）',", "collapse: '收起（也可点图标）',", 1),
    ("toggleShow: 'Show quick input (docked left of the composer)',", "toggleShow: 'Show the prompt pad',", 1),
    ("toggleHide: 'Hide quick input',", "toggleHide: 'Hide the prompt pad',", 1),
    ("toggleAria: 'Quick input',", "toggleAria: 'Prompt pad',", 1),
    ("panelAria: 'Quick input grid',", "panelAria: 'Prompt pad',", 1),
    ("collapse: 'Hide (or click ⊞)',", "collapse: 'Hide (or click the icon)',", 1),
    # 注释里的旧记号
    ("气泡是「锚在 ⊞ 旁边的浮层」", "气泡是「锚在图标旁边的浮层」", 1),
    ("⊞ 挂在 `conversation.input.left`", "开关挂在 `conversation.input.left`", 1),
    ("/** ⊞ 按钮节点：气泡靠它定位。 */", "/** 开关按钮节点：气泡靠它定位。 */", 1),
    ("默认贴在 ⊞ 右边", "默认贴在图标右边", 1),
    ("// ------------------------------------------------------------ ⊞ 开关",
     "// ------------------------------------------------------------ 入口开关", 1),
    ("// ------------------------------------------------------------ 九宫格面板",
     "// ------------------------------------------------------------ 气泡面板", 1),
    ("把 ⊞ 顶走了", "把图标顶走了", 1),
    ("// ⊞ 会被宿主布局改动", "// 图标会被宿主布局改动", 1),
    ("面板外 + ⊞ 外才算外", "面板外 + 图标外才算外", 1),
])

# ---------------------------------------------------------------- package.json
PKG = os.path.join(DEV, "package.json")
pkg = json.load(open(PKG, encoding="utf-8"))
pkg["description"] = (
    "Prompt 面板：点输入框工具行左侧的叠卡图标弹出气泡，搜索或点选预设短语，"
    "插入到草稿光标处（可撤销、不覆盖草稿）。"
    "Prompt pad beside the DSH composer: open a popover from the stacked-cards icon, "
    "search or click a saved phrase, and it is inserted at the caret as one undoable edit."
)
files = pkg["files"]
for extra in ("icon.svg", "icon-256.png", "screenshots.json"):
    if extra not in files:
        files.append(extra)
json.dump(pkg, open(PKG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(PKG, "a", encoding="utf-8").write("\n")
print("ok package.json")
print("   description:", pkg["description"][:60], "...")
print("   files:", ", ".join(pkg["files"]))

# ---------------------------------------------------------------- screenshots.json
shots = [
    "docs/01-main.png",
    "docs/03-search.png",
    "docs/04-edit-grid.png",
    "docs/02-edit-cell.png",
    "docs/05-empty-page.png",
]
open(os.path.join(DEV, "screenshots.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(shots, ensure_ascii=False, indent=2) + "\n"
)
print("ok screenshots.json ->", len(shots), "images")

# ---------------------------------------------------------------- 残留检查
bad = []
for name in ("client.js", "index.js", "package.json", "README.md", "cordis.patch.yml"):
    text = open(os.path.join(DEV, name), encoding="utf-8").read()
    for token in ("⊞", "九宫格", "常驻"):
        if token in text:
            bad.append(f"{name}: {token}")
print("\n残留可疑词:", bad if bad else "无")
