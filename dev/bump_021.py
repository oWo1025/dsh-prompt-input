# -*- coding: utf-8 -*-
"""版本升到 0.2.1（UI 打磨），让 /quick-input/health 能区分跑的是哪一份。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"

c = os.path.join(DEV, "client.js")
s = open(c, encoding="utf-8").read()
assert s.count("const CLIENT_BUILD = '0.2.0+build1'") == 1
s = s.replace("const CLIENT_BUILD = '0.2.0+build1'", "const CLIENT_BUILD = '0.2.1+build1'")
open(c, "w", encoding="utf-8", newline="\n").write(s)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.0'") == 1
s = s.replace("const VERSION = '0.2.0'", "const VERSION = '0.2.1'")
open(i, "w", encoding="utf-8", newline="\n").write(s)

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.1"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

print("versions ->", pkg["version"])
