# -*- coding: utf-8 -*-
"""0.3.1：修正强调色 token（DSH 实际发布的名字带重复后缀），并保留多级回退。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"
CLIENT = os.path.join(DEV, "client.js")
src = open(CLIENT, encoding="utf-8").read()

OLD = "var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))"
NEW = (
    "var(--dsw-alias-brand-primary-new-color,"
    "var(--dsw-alias-brand-primary-new-colorprimary-new-color,"
    "var(--dsw-alias-brand-primary,#4d6bfe)))"
)
count = src.count(OLD)
assert count == 21, count
src = src.replace(OLD, NEW)
print("accent chain fixed:", count)

assert src.count("const CLIENT_BUILD = '0.3.0+build1'") == 1
src = src.replace("const CLIENT_BUILD = '0.3.0+build1'", "const CLIENT_BUILD = '0.3.1+build1'")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.3.0'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.3.0'", "const VERSION = '0.3.1'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.3.1"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

CL = os.path.join(DEV, "CHANGELOG.md")
c = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
assert c.startswith(head)
if "0.3.1 —" not in c:
    c = head + """## 0.3.1 — 修正强调色 token

0.3.0 里用的 `--dsw-alias-brand-primary-new-color` 在已发布主题里**不存在**：实际名字是
`--dsw-alias-brand-primary-new-colorprimary-new-color`（上游变量名的重复后缀 bug），
于是整条链路回退到 `--dsw-alias-brand-primary`（近黑），界面又变回灰的。

现在改成三级回退：

```css
var(--dsw-alias-brand-primary-new-color,                 /* 若上游修正拼写 */
    var(--dsw-alias-brand-primary-new-colorprimary-new-color,  /* 当前发布的名字 */
        var(--dsw-alias-brand-primary, #4d6bfe)))          /* 兜底墨色 */
```

这样：上游改回来 → 自动用正名；没改 → 用实际存在的那个名字；两者都没有 → 退回原生墨色。

""" + c[len(head):]
    open(CL, "w", encoding="utf-8", newline="\n").write(c)

print("ok ->", pkg["version"])
