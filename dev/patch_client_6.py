# -*- coding: utf-8 -*-
"""P0.3：修底部行溢出（✎ 被裁）、页签再收一点、搜索结果选中态加强。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = r"E:\dsh\quick-input-dev\client.js"
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    assert src.count(old) == 1, f"[{label}] got {src.count(old)}"
    src = src.replace(old, new)


# 底部行：允许压缩，绝不溢出
sub(".dsq-tabsrow{display:flex;align-items:center;gap:6px;flex:none;min-width:0}",
    ".dsq-tabsrow{display:flex;align-items:center;gap:6px;flex:none;min-width:0;overflow:hidden}",
    "tabsrow")

sub(".dsq-tabs{display:flex;align-items:center;gap:4px;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none;padding:1px}",
    ".dsq-tabs{display:flex;align-items:center;gap:4px;flex:1 1 0;min-width:0;overflow-x:auto;scrollbar-width:none;padding:1px}",
    "tabs")

sub(".dsq-tab{box-sizing:border-box;flex:none;height:24px;padding:0 9px;",
    ".dsq-tab{box-sizing:border-box;flex:none;height:24px;padding:0 8px;", "tab-pad")

sub(".dsq-count{flex:none;max-width:132px;overflow:hidden;",
    ".dsq-count{flex:0 1 auto;min-width:0;max-width:120px;overflow:hidden;", "count")

# 搜索结果：选中行加左侧品牌色细条，比纯底色更明确
sub(".dsq-item-on{background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.1))}",
    ".dsq-item-on{background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.1));box-shadow:inset 2px 0 0 var(--dsw-alias-brand-primary,#4d6bfe)}",
    "item-on")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("ok, size =", len(src))
