# -*- coding: utf-8 -*-
"""0.2.8：编辑态在标题行显示说明条，替换搜索框。"""
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


# 1) 样式
sub(""".dsq-search:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));background:var(--dsw-alias-bg-layer-2,#fff);box-shadow:0 0 0 3px color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 14%,transparent)}""",
    """.dsq-search:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));background:var(--dsw-alias-bg-layer-2,#fff);box-shadow:0 0 0 3px color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 14%,transparent)}
/* 编辑态：搜索框让位给状态说明条 */
.dsq-editbar{flex:1;min-width:0;display:flex;align-items:center;gap:6px;height:30px;padding:0 10px;border:1px dashed color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 42%,transparent);border-radius:var(--dsw-radius-md,10px);background:color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 8%,transparent);color:var(--dsw-alias-label-primary,#1f2328);font-size:12px;line-height:16px}
.dsq-editbar-text{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dsq-editbar svg{flex:none;color:var(--dsw-alias-brand-primary,#4d6bfe)}""",
    "css")

# 2) 搜索框在编辑态隐藏
sub("""          { className: 'dsq-searchwrap' },""",
    """          { className: 'dsq-searchwrap', style: editMode ? { display: 'none' } : undefined },""",
    "search-hide")

# 3) 说明条插在关闭按钮之前（视觉上紧挨把手）
sub("""        h(
          'button',
          {
            type: 'button',
            className: 'dsq-x',""",
    """        editMode
          ? h(
              'div',
              { className: 'dsq-editbar', role: 'status' },
              h(PencilIcon, null),
              h('span', { className: 'dsq-editbar-text', title: t('editBarHint') }, t('editBarHint')),
            )
          : null,
        h(
          'button',
          {
            type: 'button',
            className: 'dsq-x',""",
    "editbar")

# 4) 进编辑态时清掉搜索词，否则网格会被搜索结果顶掉
sub("""              store.editing.set(sessionId, null)
              store.editMode.set(sessionId, editMode !== true)
              store.emit()""",
    """              store.editing.set(sessionId, null)
              store.editMode.set(sessionId, editMode !== true)
              if (editMode !== true) writeSearch(sessionId, { query: '', active: 0 })
              store.emit()""",
    "clear-query")

# 5) 字典
sub("""        emptyPageTitle: '这一页还空着',""",
    """        emptyPageTitle: '这一页还空着',
        editBarHint: '编辑中 · 拖动卡片调整顺序',""",
    "dict-zh")

sub("""        emptyPageTitle: 'This page is empty',""",
    """        emptyPageTitle: 'This page is empty',
        editBarHint: 'Editing · drag cards to reorder',""",
    "dict-en")

# 6) 版本
sub("const CLIENT_BUILD = '0.2.7+build1'", "const CLIENT_BUILD = '0.2.8+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.7'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.7'", "const VERSION = '0.2.8'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.8"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

print("ok ->", pkg["version"], "| size", len(src))
