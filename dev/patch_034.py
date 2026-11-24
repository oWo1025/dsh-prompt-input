# -*- coding: utf-8 -*-
"""修 RELEASE.md 的编号与多余引号；版本升到 0.3.4（图标几何 + 文案清理）。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"

# ---------------------------------------------------------------- RELEASE.md
R = os.path.join(DEV, "docs", "RELEASE.md")
r = open(R, encoding="utf-8").read()
bad = "4. 合并后站点与市场会自动重新生成并收录（通常一天内）。\n\n'\n"
assert r.count(bad) == 1, r.count(bad)
r = r.replace(bad, "4. 合并后站点与市场会自动重新生成并收录（通常一天内）。\n")
assert r.count("## 五、给上游提 PR") == 1
r = r.replace("## 五、给上游提 PR", "## 四、给上游提 PR")
assert r.count("## 六、发布到 npm（可选）") == 1
r = r.replace("## 六、发布到 npm（可选）", "## 五、发布到 npm（可选）")
open(R, "w", encoding="utf-8", newline="\n").write(r)
print("RELEASE.md fixed")

# ---------------------------------------------------------------- 版本
C = os.path.join(DEV, "client.js")
c = open(C, encoding="utf-8").read()
assert c.count("const CLIENT_BUILD = '0.3.3+build1'") == 1
open(C, "w", encoding="utf-8", newline="\n").write(
    c.replace("const CLIENT_BUILD = '0.3.3+build1'", "const CLIENT_BUILD = '0.3.4+build1'")
)

I = os.path.join(DEV, "index.js")
i = open(I, encoding="utf-8").read()
assert i.count("const VERSION = '0.3.3'") == 1
open(I, "w", encoding="utf-8", newline="\n").write(i.replace("const VERSION = '0.3.3'", "const VERSION = '0.3.4'"))

P = os.path.join(DEV, "package.json")
pkg = json.load(open(P, encoding="utf-8"))
pkg["version"] = "0.3.4"
json.dump(pkg, open(P, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(P, "a", encoding="utf-8").write("\n")

CL = os.path.join(DEV, "CHANGELOG.md")
t = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
if "0.3.4 —" not in t:
    t = head + """## 0.3.4 — 清理过时信息 + PNG 图标

- **文案**：`package.json` 描述与插件内 aria/tooltip 里残留的「⊞」「常驻在输入框左边」「九宫格」
  全部改掉——它们描述的是 0.2 之前的贴边形态。
- **图标**：新增 `icon-256.png`（位图）。精选列表要求市场图标必须是 GitHub 托管的**位图**，
  SVG 会被拒；几何与 `icon.svg` 一致，只是描边细一点、行距开一点，256px 下两行字不会糊成一块。
- **截图清单**：新增 `screenshots.json`（市场从**插件仓库**读它，而不是写进收录条目）。
- **发布文档**：`docs/RELEASE.md` 的「市场条目」一节按 awesome-dsh-plugin 的 contributing.md 重写
  （一个插件一个 YAML 文件、不手改生成的 README、不写 npm 字段、单 PR 最多 3 条）。

""" + t[len(head):]
    open(CL, "w", encoding="utf-8", newline="\n").write(t)

print("version ->", pkg["version"])
