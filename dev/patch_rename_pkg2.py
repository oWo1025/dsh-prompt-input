# -*- coding: utf-8 -*-
"""改名第二步：文档（RELEASE.md）、CHANGELOG、残留检查。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
OLD = "dsh-quick-input"
NEW = "dsh-prompt-input"
NEW_REPO = "https://github.com/oWo1025/dsh-prompt-input"

P = os.path.join(DEV, "docs", "RELEASE.md")
s = open(P, encoding="utf-8").read()

# 1) 克隆上游 fork 的地址：fork 保留上游原名，不要跟着改
s = s.replace(
    "https://github.com/oWo1025/dsh-quick-input-upstream.git",
    "https://github.com/oWo1025/dsh-quick-input.git",
)
# 2) install 里的 github: spec
assert s.count("github:oWo1025/dsh-quick-input") == 1
s = s.replace("github:oWo1025/dsh-quick-input", "github:oWo1025/dsh-prompt-input")
# 3) raw 图床地址
assert s.count("raw.githubusercontent.com/oWo1025/dsh-quick-input/") == 2
s = s.replace(
    "raw.githubusercontent.com/oWo1025/dsh-quick-input/",
    "raw.githubusercontent.com/oWo1025/dsh-prompt-input/",
)
# 4) 我们自己的仓库地址（先把“上游 fork 的克隆地址”占位，避免被一起替换）
CLONE = "https://github.com/oWo1025/dsh-quick-input.git"
assert s.count(CLONE) == 1
s = s.replace(CLONE, "@@CLONE@@")
assert s.count("https://github.com/oWo1025/dsh-quick-input") == 1
s = s.replace("https://github.com/oWo1025/dsh-quick-input", NEW_REPO)
s = s.replace("@@CLONE@@", CLONE)
# 5) 本地路径
s = s.replace("git -C E:/dsh/quick-input-dev", "git -C E:/dsh/dsh-prompt-input")

# 6) 重写「包名」一节：已定名
start = s.index("## 二、包名")
end = s.index("## 三、市场条目")
s = s[:start] + """## 二、包名

已定名 **`dsh-prompt-input`**（v0.3.0 起）。上游 `dsh-quick-input` 这个 npm 名属于原作者，
换名之后两者彻底分开，可以各自发版。

改名连带改了四处，缺一个都会出问题：

| 位置 | 值 | 说明 |
|---|---|---|
| `package.json` `name` | `dsh-prompt-input` | 插件目录名 |
| `client.js` 模块 id | `dsh-prompt-input` | **必须等于包名**，浏览器半区靠它注册 |
| `cordis.patch.yml` 行 `name` | `dsh-prompt-input` | 告诉 Loader 加载哪个包 |
| `README` / 条目 `url` | 新仓库地址 | 市场页面的链接 |

**不受影响**（改名只动"包"，不动"数据"）：`%DSH_HOME%\\quick-input\\presets.json`、
路由 `/quick-input/*`、`localStorage` 的 `quick-input.pos.v1` / `quick-input.recent.v1`。
所以已经填好的 prompt、面板位置、最近使用都还在。

改名之后必须**卸载旧包再装新包**：两者注册同一个插件行 id（`quick-input`），同时存在会撞 id。

""" + s[end:]
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok docs/RELEASE.md")

# ---------------------------------------------------------------- CHANGELOG
CL = os.path.join(DEV, "CHANGELOG.md")
c = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
assert c.startswith(head)
if "0.3.0 — 改名" not in c:
    c = head + """## 0.3.0 — 改名 dsh-prompt-input

- 包名 `dsh-quick-input` → **`dsh-prompt-input`**，与上游彻底分开（npm 上原名属于原作者）。
- 连带改动：客户端模块 id（`window.__ModuleLoader__.load({ id })` 必须等于包名）、
  `cordis.patch.yml` 的行 `name`、`package.json` 的 `repository` / `homepage` / `bugs`。
- **数据位置不变**：仍是 `%DSH_HOME%\\quick-input\\presets.json`，路由仍是 `/quick-input/*`，
  `localStorage` 键也不变——已填的 prompt、面板位置、最近使用都不受影响。
- 升级方式：卸载旧包 → 从新目录安装。新旧包注册同一个插件行 id，不能并存。

""" + c[len(head):]
    open(CL, "w", encoding="utf-8", newline="\n").write(c)
print("ok CHANGELOG")

# ---------------------------------------------------------------- 残留检查
left = []
for root, dirs, files in os.walk(DEV):
    if ".git" in root:
        continue
    for name in files:
        if not name.endswith((".js", ".json", ".yml", ".md", ".py", ".svg", ".cjs")):
            continue
        p = os.path.join(root, name)
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for line in text.splitlines():
            if OLD in line:
                left.append(f"{os.path.relpath(p, DEV)}: {line.strip()[:100]}")
print(f"\n剩余 {OLD} 共 {len(left)} 处（应全部是上游引用 / 历史记录）：")
for item in left:
    print("  ", item)
