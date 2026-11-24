# -*- coding: utf-8 -*-
"""把 docs/RELEASE.md 的「市场条目 / 上架步骤」改成 contributing.md 的真实格式。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"E:\dsh\dsh-prompt-input\docs\RELEASE.md"
s = open(P, encoding="utf-8").read()

start = s.index("## 三、市场条目")
end = s.index("## 五、给上游提 PR")

NEW = '''## 三、市场条目（真实格式）

市场列表来自 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)。
按它的 [contributing.md](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/blob/main/contributing.md)：

> **两个 README 由脚本生成，请勿手工编辑。** 列表数据在 `data/plugins/`，一个插件一个 YAML 文件。

### 要提交的文件

路径：`data/plugins/<owner>__<repo>.yml` → 我们的是 **`data/plugins/oWo1025__dsh-prompt-input.yml`**

```yaml
url: https://github.com/oWo1025/dsh-prompt-input
name: oWo1025/dsh-prompt-input
category: ui
description:
  en: 'Prompt pad beside the DSH composer: open a popover from the stacked-cards icon, search or click a saved phrase, and it is inserted at the caret as one undoable edit. Adds hover preview, a recent-used page, drag-to-reorder and a global hotkey. Fork of dsh-quick-input (MIT, cm860712ch-cloud); the UI layer has been rewritten.'
  zh: 'DSH 输入框旁的 Prompt 面板：点叠卡图标弹出气泡，搜索或点选预设短语，插入到草稿光标处（可撤销、不覆盖草稿）。含悬停预览、最近使用、拖动排序与全局快捷键。基于 dsh-quick-input（MIT，cm860712ch-cloud）二次开发，界面与交互层已重写。'
icon: https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/icon-256.png
```

⚠️ **描述里含 `: `（冒号加空格）必须加引号**，否则 YAML 会当成嵌套键。上面两行都加了。

### 分类

`category: ui`（界面增强）。合法取值见 contributing.md 的分类列表，共 24 个。

### 要求（逐条对照）

| 要求 | 我们 |
|---|---|
| `package.json` 声明 **`dsh.bundle`**（只声明 `dsh.client` 会被拒，这是最常见的退回原因） | ✅ `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }` |
| 插件真实可运行（不是空壳） | ✅ 这套已经在你机器上日常在用 |
| 仓库至少存在 1 天（未满会被自动重新检查） | ⚠️ 仓库是今天建的/改名的，**第一天会被这条挡住**，隔天再提 |
| GitHub 仓库加 `dsh-plugin` topic | ⬜ 待做（仓库页右上 About → 齿轮 → Topics） |
| 发 npm 的话，`repository` 要指回被收录的仓库 | ✅ 已指向本仓库；不发 npm 则无所谓 |
| 单条描述不夸大、不写营销话术 | ✅ 只写功能与 fork 关系 |
| 一个 PR 最多 3 条 | ✅ 我们只提 1 条 |

### 截图：放在**我们自己仓库**的 `screenshots.json`

不是写进 YAML。在 package.json 旁边放一个 `screenshots.json`，内容是相对路径数组（1–8 张），
市场会去读：

```json
["docs/01-main.png", "docs/03-search.png", "docs/04-edit-grid.png", "docs/02-edit-cell.png", "docs/05-empty-page.png"]
```

仓库里已经有这个文件了。也可以用绝对地址，但必须是 GitHub 托管的。

### 图标：必须是位图

contributing.md 明确要求 **GitHub 托管的位图**（png/jpg/webp），**SVG 会被拒**，尺寸按 ~96px 方图设计。
所以我们在 `icon.svg` 之外另存了 `icon-256.png`，条目里指向它。

### 不要做的事

- ❌ 不要手工编辑那两个生成的 README（会被脚本覆盖，PR 也容易冲突）
- ❌ 不要自己往 YAML 里写 `npm:` 字段（会被拒）
- ❌ 不要往 `dsh-market` 那个市场仓库提条目——它的 README 写着"这个仓库是市场应用本身，不是插件目录"
- ❌ 不要一次提超过 3 条

### 提交方式

1. Fork [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)。
2. 新建 `data/plugins/oWo1025__dsh-prompt-input.yml`，内容照上面。
3. 提 PR，标题就叫 `Add dsh-prompt-input`，正文写一句它做什么 + 明确说明是 fork。
4. 合并后站点与市场会自动重新生成并收录（通常一天内）。

'

''' + s[end:]

s = s[:start] + NEW
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("RELEASE.md rewritten:", len(s), "chars")
