# -*- coding: utf-8 -*-
"""按 dsh-plugin-market 的规则模拟检索，检验描述的词覆盖。"""
import io
import json
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ENTRY = json.load(open(r"E:\dsh\dsh-prompt-input\docs\market-entry.yml.json", encoding="utf-8")) \
    if False else None

# 直接从 yml 里取内容（避免额外依赖）
import subprocess

yaml_text = open(r"E:\dsh\dsh-prompt-input\docs\market-entry.yml", encoding="utf-8").read()
def field(name):
    m = re.search(rf"^\s*{name}:\s*'?(.*?)'?$", yaml_text, re.M)
    return m.group(1) if m else ""

INDEX_TEXT = " ".join([
    "oWo1025/dsh-prompt-input",            # 条目名 / 标题
    "oWo1025",                              # 作者
    field("en"),                            # description.en
    field("zh"),                            # description.zh
    "UI 增强 UI Enhancements",              # 分类标题
])

CJK = r"\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"


def tokens(text):
    text = unicodedata.normalize("NFKC", text).lower()
    out = set()
    for run in re.findall(rf"[a-z0-9{CJK}]+", text):
        if re.fullmatch(rf"[{CJK}]+", run):
            if len(run) == 1:
                out.add(run)
            else:
                for i in range(len(run) - 1):
                    out.add(run[i:i + 2])
                out.add(run[-1])
        else:
            out.add(run)
    return out


def lev(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def hit(word, index):
    if any(t.startswith(word) or word.startswith(t) for t in index):
        return True
    if len(word) >= 4:
        limit = min(2, max(1, round(len(word) / 5)))
        for t in index:
            if abs(len(t) - len(word)) <= limit and lev(word, t) <= limit:
                return True
    return False


INDEX = tokens(INDEX_TEXT)
print(f"索引词 {len(INDEX)} 个\n")

QUERIES = [
    # 中文
    "快捷输入", "快捷", "输入", "提示词", "预设", "短语", "话术", "模板",
    "常用指令", "最近使用", "搜索", "撤销", "快捷键", "插入", "面板", "管理",
    # 英文
    "prompt", "prompts", "prompt library", "prompt manager", "snippet", "snippets",
    "quick input", "quick phrases", "template", "templates", "presets", "composer",
    "insert", "hotkey", "library", "pad",
    # 混合 / 长尾
    "prompt 管理", "快捷输入 prompt", "快捷短语", "话术库", "提示词库", "模板库", "指令", "ds prompt",
]

fails = []
for q in QUERIES:
    words = list(tokens(q))
    ok = all(hit(w, INDEX) for w in words)
    print(f"{'OK  ' if ok else 'MISS'} {q:<22}{'  ' + ' '.join(w for w in words if not hit(w, INDEX)) if not ok else ''}")
    if not ok:
        fails.append((q, [w for w in words if not hit(w, INDEX)]))

print(f"\n命中 {len(QUERIES) - len(fails)}/{len(QUERIES)}")
if fails:
    print("未覆盖：")
    for q, ws in fails:
        print(f"  {q}  -> 缺 {ws}")
