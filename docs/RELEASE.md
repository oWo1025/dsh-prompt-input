# 发布与上架清单

> 这份文件记录"要把这个插件发出去"需要做的事：署名、市场条目、给上游提 PR。
> 每一步都写清楚要改哪个文件、改成什么。

---

## 一、发布前必须确认

| 项 | 现状 | 说明 |
|---|---|---|
| `LICENSE` | ✅ 已含两行版权 | MIT 要求保留原版权声明；已补充修改方声明 |
| `package.json` `author` | ✅ `oWo1025` | 修改方 |
| `package.json` `contributors` | ✅ 含原作者 | 署名上游 |
| `package.json` `repository` / `homepage` / `bugs` | ✅ 指向本仓库 | 不要留着上游地址 |
| `README` 来源章节 | ✅ 已写明 fork 与保留/重写范围 | 市场页面会读 README |
| `README` 语言 | ✅ 中文为正文，顶部三行英文摘要 | 英文界面用户的详情页也读得到（见下） |
| `icon.svg` | ✅ 自绘（叠卡） | 不要用上游的品牌素材 |
| 版本号 | `0.4.3` | 语义化：功能加版本 |
| `engines` / peer 声明 | 未声明 | 市场会显示"兼容性未知"，若要显示需补 `engines.dsh` |

## 二、包名

已定名 **`dsh-prompt-input`**（v0.3.0 起）。上游 `dsh-quick-input` 这个 npm 名属于原作者，
换名之后两者彻底分开，可以各自发版。

改名连带改了四处，缺一个都会出问题：

| 位置 | 值 | 说明 |
|---|---|---|
| `package.json` `name` | `dsh-prompt-input` | 插件目录名 |
| `client.js` 模块 id | `dsh-prompt-input` | **必须等于包名**，浏览器半区靠它注册 |
| `cordis.patch.yml` 行 `name` | `dsh-prompt-input` | 告诉 Loader 加载哪个包 |
| `README` / 条目 `url` | 新仓库地址 | 市场页面的链接 |

**不受影响**（改名只动"包"，不动"数据"）：`%DSH_HOME%\quick-input\presets.json`、
路由 `/quick-input/*`、`localStorage` 的 `quick-input.pos.v1` / `quick-input.recent.v1`。
所以已经填好的 prompt、面板位置、最近使用都还在。

改名之后必须**卸载旧包再装新包**：两者注册同一个插件行 id（`quick-input`），同时存在会撞 id。

## 三、市场条目（真实格式）

市场列表来自 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)。
按它的 [contributing.md](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/blob/main/contributing.md)：

> **两个 README 由脚本生成，请勿手工编辑。** 列表数据在 `data/plugins/`，一个插件一个 YAML 文件。

> 可直接复制仓库里的 docs/market-entry.yml（内容与下面一致，已用 js-yaml 验证可解析）。

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

### 搜索曝光（写在描述里，不是堆关键词）

市场的检索规则（`dsh-plugin-market` 文档）：文本匹配**包名、作者、标题、描述、分类标题**；
按非字母数字切词，中日韩文本切成**相邻两字组**；查询里的**每个词都要命中**（AND），
支持前缀匹配，四字以上才允许轻微编辑距离。名称/标题权重 ×3。

索引条目里**没有 keywords 字段**，所以曝光只能靠：**描述措辞、条目名、分类**。当前覆盖的词：

| 语言 | 覆盖 |
|---|---|
| 中文 | 快捷输入、预设、短语、话术、模板、提示词、常用指令、收藏、最近使用、搜索、插入、光标、快捷键、撤销、草稿 |
| 英文 | prompt, prompts, prompt manager, prompt library, quick input, quick phrases, snippets, templates, presets, composer, insert at caret, undoable, hotkey, fork |

维护时注意三点：

1. **中文要写完整的词**——切成两字组后，「快捷输入」产生 快捷/捷输/输入，查「输入」也能中；
   但如果只写「快捷」，查「快捷输入」就缺 捷输、输入 两个组，不会命中。
2. **别删英文同义词**：`snippets` / `templates` / `quick phrases` 都有人在查。
3. **描述必须还是人话**：堆词会被审核打回，也影响点击率。上面两段是自然句子，不是关键词表。

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

### README 语言策略（详情页上用户看到什么）

市场里有两处文字，来源完全不同，别混：

| 位置 | 文字来源 | 跟随界面语言？ | 改了要不要重新提 PR |
|---|---|---|---|
| 卡片（浏览、搜索、分类列表） | 条目里的 `description.zh` / `.en` | ✅ 会（dshmarket 文档：「中英描述跟随界面语言」） | **要**——条目是快照 |
| 详情页 / 安装弹窗 / 站点插件页 | 从**你仓库的 README** 抽取（条目里没策展详细介绍文档时） | ❌ 不跟随，只读 README 本身 | **不要**——合并后每次实时读 |

所以 README 的写法决定了英文界面用户点进去看到什么。当前策略：

- **中文是正文主体**（220 行，全中文），结构、截图、用法都在中文里；
- **标题下三行英文块**：是什么、怎么装、并注明「正文为中文」；
- **不用 `<details>` 折叠英文块**——市场的 Markdown 渲染器未必保留原生 HTML，一旦被过滤，整段就没了；`blockquote` 是标准 Markdown，一定渲染；
- **不翻译全文**——两份文档一旦不同步，比只有一份更糟；摘要 + 语言说明的性价比最高。

两个必须记住的点：

1. 这段英文**不提升搜索曝光**。市场索引只读条目的 `description`，**不索引 README 正文**。
   它的作用只是留住英文用户（别让他们点进来一脸中文地退出去）。
2. 换截图、改 README、换 icon **都不用重新提 PR**——它们都是链接/实时读取；
   只有 `description` / `category` / `name` 这类**条目字段**改了才需要再提一个 PR。

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

## 四、给上游提 PR

上游仓库：<https://github.com/cm860712ch-cloud/dsh-quick-input>（默认内容与我们仓库根目录的
`upstream-0.1.0` 标签一致）。

**现实建议**：上千行的 UI 重写，一次 PR 很难被合并。建议先开 issue 说明动机，再拆成小 PR：

1. **槽位迁移 + 气泡化**（`conversation.input.overlay` → `shell.overlay`，去掉量宿主 DOM 的逻辑）
2. **搜索 + 键盘**
3. **悬停预览 / 拖拽位置记忆 / 快捷键**
4. **最近使用 / 编辑态排序**

第一条就足够独立成 PR，也最容易说服人（它修的是宿主契约问题，不是口味问题）。

### 具体操作

```bash
# 1) fork 上游后克隆你的 fork
git clone https://github.com/oWo1025/dsh-quick-input.git upstream-pr
cd upstream-pr
git remote add upstream https://github.com/cm860712ch-cloud/dsh-quick-input.git
git fetch upstream

# 2) 从上游默认分支开一个新分支
git checkout -b feat/popover-ui upstream/HEAD

# 3) 只把运行时文件的变化打过去（不要带 README 重写、dev 脚本、版本号）
#    在本仓库执行，产出补丁：
git -C E:/dsh/dsh-prompt-input diff upstream-0.1.0 HEAD -- client.js index.js icon.svg > popover.patch

# 4) 应用并自己验一遍
git apply --stat popover.patch
git apply popover.patch
node --check client.js

# 5) 提交、推到你的 fork、开 PR
git commit -am "feat(ui): open the pad as a popover anchored to the toggle"
git push -u origin feat/popover-ui
```

PR 描述里写三件事：**问题**（固定槽位 + 量宿主 DOM 违反插件规范、面板被裁）、
**做法**（迁到 `shell.overlay`、去掉 DOM 探测）、**验证**（刷新后的截图 + `node --check`）。
不要夹带改名、版本号、README 重写——那些属于你自己的发行版。

## 五、发布到 npm（可选）

```bash
npx tsc -v                 # 本项目无构建步骤，纯 JS
npm whoami                 # 确认登录
npm publish --access public
```

发布前把 `package.json` 的 `files` 收紧（当前已排除 `dev/`、`docs/`），并确认 `name` 已改。
