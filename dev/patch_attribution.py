# -*- coding: utf-8 -*-
"""署名字段改成 fork 作者：LICENSE / package.json / README。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
REPO = "https://github.com/oWo1025/dsh-quick-input"

# ---------------------------------------------------------------- LICENSE
LIC = os.path.join(DEV, "LICENSE")
license_text = """MIT License

Copyright (c) 2026 cm860712ch-cloud (original work: dsh-quick-input)
Copyright (c) 2026 oWo1025 (modifications: popover UI, search, recent-used page,
                                drag & drop, edit-mode reordering)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
open(LIC, "w", encoding="utf-8", newline="\n").write(license_text)
print("LICENSE updated")

# ---------------------------------------------------------------- package.json
PKG = os.path.join(DEV, "package.json")
pkg = json.load(open(PKG, encoding="utf-8"))
pkg["author"] = "oWo1025"
pkg["contributors"] = ["cm860712ch-cloud (original dsh-quick-input)"]
pkg["repository"] = {"type": "git", "url": "git+" + REPO + ".git"}
pkg["homepage"] = REPO + "#readme"
pkg["bugs"] = {"url": REPO + "/issues"}
json.dump(pkg, open(PKG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(PKG, "a", encoding="utf-8").write("\n")
print("package.json:", pkg["author"], "|", pkg["repository"]["url"])

# ---------------------------------------------------------------- README
README = os.path.join(DEV, "README.md")
s = open(README, encoding="utf-8").read()
old_start = "## 九、来源与许可"
idx = s.index(old_start)
new_section = """## 九、来源与许可

本项目是 [dsh-quick-input](https://github.com/cm860712ch-cloud/dsh-quick-input)（MIT，
© 2026 cm860712ch-cloud）的**衍生版本**，不是上游官方发布。

保留自上游的部分：

- 宿主半区 `index.js`（预设落盘与 `/quick-input/*` 路由）与 `presets.js` 的规范化逻辑
- `presets.json` 的数据结构（每页 9 格、最多 12 页、`label` ≤12 字、`text` ≤2000 字）
- 编辑器的基本交互（改名、改内容、清空、增删页）

本仓库重写的部分：

- 渲染槽位：`conversation.input.overlay` → `shell.overlay`
- 面板形态：贴边常驻 → 锚定气泡（可拖动、位置记忆）
- 新增：搜索、悬停预览、最近使用、编辑态拖动排序、跨页移动、另存为新格、全局快捷键
- 全部视觉与图标

原始版权声明与许可全文见 [LICENSE](LICENSE)；本仓库的修改同样以 MIT 发布。
上游若发布新版本，可以 `git remote add upstream` 后合并——本仓库的历史保留了
`upstream-0.1.0` 标签作为逐字节基线。
"""
s = s[:idx] + new_section
open(README, "w", encoding="utf-8", newline="\n").write(s)
print("README fork section rewritten, chars:", len(s))
