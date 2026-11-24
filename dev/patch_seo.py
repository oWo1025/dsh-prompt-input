# -*- coding: utf-8 -*-
"""搜索曝光优化：重写市场条目描述（中英双语词覆盖）、扩充 keywords、文档记录词表。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"

EN = (
    "Prompt pad and prompt manager for the DSH composer: a quick-input popover with a searchable "
    "library of saved prompts, snippets, quick phrases and reusable templates. Click a card to insert "
    "the text at the caret as one undoable edit. Includes presets pages, a recent-used page, hover preview, "
    "drag-to-reorder, favorites-style pinning and a global hotkey. Fork of dsh-quick-input "
    "(MIT, cm860712ch-cloud); the UI layer has been rewritten."
)

ZH = (
    "DSH 输入框旁的快捷输入面板，也是一个提示词（prompt）管理工具：气泡里搜索预设、短语、话术、"
    "常用指令与模板，点一张卡片就把文字插入到光标处，可撤销、不覆盖草稿。含快捷短语编辑、多页预设、"
    "最近使用、悬停预览、拖动排序与全局快捷键。基于 dsh-quick-input（MIT，cm860712ch-cloud）二次开发，"
    "界面与交互层已重写。"
)

# ---------------------------------------------------------------- 市场条目
P = os.path.join(DEV, "docs", "market-entry.yml")
lines = [
    "url: https://github.com/oWo1025/dsh-prompt-input",
    "name: oWo1025/dsh-prompt-input",
    "category: ui",
    "description:",
    f"  en: '{EN}'",
    f"  zh: '{ZH}'",
    "icon: https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/icon-256.png",
]
open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("market-entry.yml rewritten:", len(EN), "en chars /", len(ZH), "zh chars")

# ---------------------------------------------------------------- keywords
PKG = os.path.join(DEV, "package.json")
pkg = json.load(open(PKG, encoding="utf-8"))
kws = [
    "deepseek",
    "deepseek-harness",
    "dsh",
    "dsh-plugin",
    "dsh-client",
    "client-plugin",
    "prompt",
    "prompts",
    "prompt-library",
    "prompt-manager",
    "snippets",
    "quick-input",
    "quick-phrases",
    "quick-reply",
    "phrase-library",
    "presets",
    "templates",
    "composer",
    "i18n",
]
pkg["keywords"] = kws
json.dump(pkg, open(PKG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(PKG, "a", encoding="utf-8").write("\n")
print("keywords:", len(kws))

# ---------------------------------------------------------------- 文档：词表与理由
R = os.path.join(DEV, "docs", "RELEASE.md")
r = open(R, encoding="utf-8").read()
anchor = "### 截图：放在**我们自己仓库**的 `screenshots.json`"
assert r.count(anchor) == 1
block = """### 搜索曝光（写在描述里，不是堆关键词）

市场的检索规则（`dsh-plugin-market` 文档）：文本匹配**包名、作者、标题、描述、分类标题**；
按非字母数字切词，中日韩文本切成**相邻两字组**；查询里的**每个词都要命中**（AND），
支持前缀匹配，四字以上才允许轻微编辑距离。名称/标题权重 ×3。

索引条目里**没有 keywords 字段**，所以曝光只能靠：**描述措辞、条目名、分类**。当前覆盖的词：

| 语言 | 覆盖 |
|---|---|
| 中文 | 快捷输入、预设、短语、话术、模板、提示词、常用指令、收藏、最近使用、搜索、插入、光标、快捷键、撤销、草稿 |
| 英文 | prompt, prompts, prompt manager, prompt library, quick input, quick phrases, snippets, templates, presets, composer, insert at caret, undoable, hotkey, fork |

维护时注意三点：

1. **中文要写完整的词**——切成两字组后，「快捷输入」产生 快捷/捷输/输入，查「输入」也能中；
   但如果只写「快捷」，查「快捷输入」就缺 捷输、输入 两个组，不会命中。
2. **别删英文同义词**：`snippets` / `templates` / `quick phrases` 都有人在查。
3. **描述必须还是人话**：堆词会被审核打回，也影响点击率。上面两段是自然句子，不是关键词表。

"""
r = r.replace(anchor, block + anchor)
open(R, "w", encoding="utf-8", newline="\n").write(r)
print("RELEASE.md search section added")

# 用 js-yaml 复验
print("\n--- 校验 ---")
