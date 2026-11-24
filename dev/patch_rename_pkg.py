# -*- coding: utf-8 -*-
"""改名：包名 dsh-prompt-input（代码 id / 清单 / 文档 / 版本 0.3.0）。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
OLD = "dsh-quick-input"
NEW = "dsh-prompt-input"
OLD_REPO = "https://github.com/oWo1025/dsh-quick-input"
NEW_REPO = "https://github.com/oWo1025/dsh-prompt-input"


def edit(name, pairs):
    path = os.path.join(DEV, name)
    text = open(path, encoding="utf-8").read()
    for old, new, expect in pairs:
        got = text.count(old)
        assert got == expect, f"{name}: {old[:40]!r} expected {expect} got {got}"
        text = text.replace(old, new)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("ok", name)


# ---------------------------------------------------------------- 代码
edit("client.js", [
    ("id: 'dsh-quick-input',", "id: 'dsh-prompt-input',", 1),
    ("const CLIENT_BUILD = '0.2.9+build1'", "const CLIENT_BUILD = '0.3.0+build1'", 1),
])

edit("cordis.patch.yml", [
    ("      name: 'dsh-quick-input'", "      name: 'dsh-prompt-input'", 1),
])

edit("index.js", [
    ("const VERSION = '0.2.9'", "const VERSION = '0.3.0'", 1),
])

# ---------------------------------------------------------------- package.json
PKG = os.path.join(DEV, "package.json")
pkg = json.load(open(PKG, encoding="utf-8"))
assert pkg["name"] == OLD
pkg["name"] = NEW
pkg["version"] = "0.3.0"
pkg["repository"] = {"type": "git", "url": "git+" + NEW_REPO + ".git"}
pkg["homepage"] = NEW_REPO + "#readme"
pkg["bugs"] = {"url": NEW_REPO + "/issues"}
json.dump(pkg, open(PKG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(PKG, "a", encoding="utf-8").write("\n")
print("ok package.json ->", pkg["name"], pkg["version"])

# ---------------------------------------------------------------- 文档里的“我们自己的仓库地址”
edit("docs/RELEASE.md", [
    (OLD_REPO, NEW_REPO, 4),                     # url / install / icon / screenshots
    ("github:oWo1025/dsh-quick-input", "github:oWo1025/dsh-prompt-input", 1),
    ("https://github.com/oWo1025/dsh-quick-input-upstream.git", "https://github.com/oWo1025/dsh-quick-input.git", 1),
    ("git -C E:/dsh/quick-input-dev", "git -C E:/dsh/dsh-prompt-input", 1),
])
print("ok docs/RELEASE.md")

# ---------------------------------------------------------------- dev 脚本里的固定路径
edit("dev/diff-summary.py", [
    (r"node_modules\dsh-quick-input\client.js", r"node_modules\dsh-prompt-input\client.js", 1),
])
edit("dev/patch_attribution.py", [
    ('REPO = "https://github.com/oWo1025/dsh-quick-input"',
     'REPO = "https://github.com/oWo1025/dsh-prompt-input"', 1),
])
print("ok dev scripts")

# ---------------------------------------------------------------- CHANGELOG
CL = os.path.join(DEV, "CHANGELOG.md")
s = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
assert s.startswith(head)
entry = """## 0.3.0 — 改名 dsh-prompt-input

- 包名 `dsh-quick-input` → **`dsh-prompt-input`**，与上游彻底分开（npm 上原名属于原作者）。
- 连带改动：客户端模块 id（`window.__ModuleLoader__.load({ id })` 必须等于包名）、
  `cordis.patch.yml` 的行 `name`、`package.json` 的 `repository` / `homepage` / `bugs`。
- **数据位置不变**：仍是 `%DSH_HOME%\\quick-input\\presets.json`，路由仍是 `/quick-input/*`，
  `localStorage` 键也不变——26 条 prompt、面板位置、最近使用都不受影响。
- 升级方式：卸载旧包 → 从新目录安装。旧包与新包会注册同一个插件行 id，不能并存。

"""
s = head + entry + s[len(head):]
open(CL, "w", encoding="utf-8", newline="\n").write(s)
print("ok CHANGELOG")

# ---------------------------------------------------------------- 残留检查（上游引用应保留）
left = []
for root, dirs, files in os.walk(DEV):
    if ".git" in root:
        continue
    for name in files:
        if not name.endswith((".js", ".json", ".yml", ".md", ".py", ".svg", "")):
            continue
        p = os.path.join(root, name)
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for line in text.splitlines():
            if OLD in line:
                left.append(f"{os.path.relpath(p, DEV)}: {line.strip()[:110]}")
print(f"\n剩余 {OLD} 出现 {len(left)} 处（应全部是“上游”引用）：")
for item in left:
    print("  ", item)
