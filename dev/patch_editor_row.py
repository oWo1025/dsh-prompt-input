# -*- coding: utf-8 -*-
"""0.3.2：修编辑器的「删页」按钮被挤换行 + 与「名称/内容」标签对齐。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"
CLIENT = os.path.join(DEV, "client.js")
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    got = src.count(old)
    assert got == 1, f"[{label}] expected 1 got {got}"
    src = src.replace(old, new)


# 1) 样式：行内输入可以收缩，按钮不换行
sub(""".dsq-row{display:flex;align-items:center;gap:6px}""",
    """.dsq-row{display:flex;align-items:center;gap:6px}
.dsq-row .dsq-input{flex:1;min-width:0;width:auto}""",
    "css-row")

sub(""".dsq-action{box-sizing:border-box;height:28px;padding:0 12px;""",
    """.dsq-action{box-sizing:border-box;flex:none;white-space:nowrap;height:28px;padding:0 12px;""",
    "css-action")

# 2) PageRow：标签独占一行，输入框与「删页」并排（和「名称/内容」一致）
sub("""      return h(
        'div',
        { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        h(
          'div',
          { className: 'dsq-row' },
          h('span', { className: 'dsq-row-label' }, t('pageName')),
          h('input', {
            className: 'dsq-input',
            value: title,
            maxLength: 40,
            onChange: (event) => setTitle(event.target.value),
            onBlur: rename,
            onKeyDown: (event) => {
              if (event.key === 'Enter') rename()
            },
          }),
          h(
            'button',
            {
              type: 'button',
              className: 'dsq-action',
              disabled: busy || store.doc.pages.length <= 1,
              title: store.doc.pages.length <= 1 ? t('deletePageHint') : `${t('deletePage')}: ${store.doc.pages[props.page]?.title ?? ''}`,
              onClick: removePage,
            },
            t('deletePage'),
          ),
        ),""",
    """      return h(
        'div',
        { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        h('div', { className: 'dsq-row' }, h('span', { className: 'dsq-row-label' }, t('pageName'))),
        h(
          'div',
          { className: 'dsq-row' },
          h('input', {
            className: 'dsq-input',
            value: title,
            maxLength: 40,
            onChange: (event) => setTitle(event.target.value),
            onBlur: rename,
            onKeyDown: (event) => {
              if (event.key === 'Enter') rename()
            },
          }),
          h(
            'button',
            {
              type: 'button',
              className: 'dsq-action',
              disabled: busy || store.doc.pages.length <= 1,
              title: store.doc.pages.length <= 1 ? t('deletePageHint') : `${t('deletePage')}: ${store.doc.pages[props.page]?.title ?? ''}`,
              onClick: removePage,
            },
            t('deletePage'),
          ),
        ),""",
    "page-row")

# 3) 版本
sub("const CLIENT_BUILD = '0.3.1+build1'", "const CLIENT_BUILD = '0.3.2+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.3.1'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.3.1'", "const VERSION = '0.3.2'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.3.2"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

CL = os.path.join(DEV, "CHANGELOG.md")
c = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
if "0.3.2 —" not in c:
    c = head + """## 0.3.2 — 编辑器排版修正（真机截图发现）

- 「删页」按钮被挤成两行（`删` / `页`）：行内 `input` 的 `width:100%` 把按钮顶出了容器。
  现在 `.dsq-row .dsq-input{flex:1;min-width:0;width:auto}`，按钮 `flex:none;white-space:nowrap`。
- 「页名」标签改为独占一行，与编辑器里的「名称 / 内容」一致；输入框与「删页」并排。

""" + c[len(head):]
    open(CL, "w", encoding="utf-8", newline="\n").write(c)

print("ok ->", pkg["version"])
