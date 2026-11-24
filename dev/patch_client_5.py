# -*- coding: utf-8 -*-
"""P0.2：卡片降低/顶端对齐、页签选中态改成品牌色胶囊、内容区随之定高。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = r"E:\dsh\quick-input-dev\client.js"
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    assert src.count(old) == 1, f"[{label}] got {src.count(old)}"
    src = src.replace(old, new)


sub("grid-auto-rows:54px;gap:6px;height:174px",
    "grid-auto-rows:52px;gap:6px;height:168px", "grid")

sub(".dsq-results{display:flex;flex-direction:column;gap:2px;height:174px",
    ".dsq-results{display:flex;flex-direction:column;gap:2px;height:168px", "results")

sub("align-items:flex-start;justify-content:center;padding:6px 8px;border:1px solid var(--dsw-alias-border-l1",
    "align-items:flex-start;justify-content:flex-start;padding:7px 8px;border:1px solid var(--dsw-alias-border-l1",
    "card")

sub(".dsq-tab-on{background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.12));border-color:var(--dsw-alias-border-l2,rgba(0,0,0,.12));color:var(--dsw-alias-label-primary,#1f2328);font-weight:600}",
    ".dsq-tab-on{background:color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 10%,transparent);border-color:color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 26%,transparent);color:var(--dsw-alias-label-primary,#1f2328);font-weight:600}",
    "tab-on")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("ok, size =", len(src))
