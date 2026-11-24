# -*- coding: utf-8 -*-
"""smoke.cjs 跟随 0.4.0 的命名空间改名。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"E:\dsh\dsh-prompt-input\dev\smoke.cjs"
s = open(P, encoding="utf-8").read()

pairs = [
    ("const zh = dicts['quick-input'] && dicts['quick-input'].zh\n"
     "const en = dicts['quick-input'] && dicts['quick-input'].en\n",
     "const NS_ID = 'dsh-prompt-input'\n"
     "const zh = dicts[NS_ID] && dicts[NS_ID].zh\n"
     "const en = dicts[NS_ID] && dicts[NS_ID].en\n"),
    ("ok('shortcut id', cmd.id === 'quick-input.toggle', cmd.id)",
     "ok('shortcut id', cmd.id === NS_ID + '.toggle', cmd.id)"),
]
for old, new in pairs:
    assert s.count(old) == 1, (old[:40], s.count(old))
    s = s.replace(old, new)
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("smoke.cjs updated")
