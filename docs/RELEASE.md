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
| `icon.svg` | ✅ 自绘（叠卡） | 不要用上游的品牌素材 |
| 版本号 | `0.2.9` | 语义化：功能加版本 |
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

## 三、市场条目

市场（dshmarket）自己不存插件列表，它读精选列表 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)
生成的索引。一条条目大致是这些字段（照该仓库的提交格式填，字段语义如下）：

```json
{
  "name": "dsh-prompt-pad",
  "owner": "oWo1025",
  "url": "https://github.com/oWo1025/dsh-prompt-input",
  "category": "ui",
  "description": {
    "zh": "DSH 输入框旁的 prompt 面板：点叠卡图标弹出气泡，搜索或点选预设短语，文字插入光标处（可撤销、不覆盖草稿）。含悬停预览、最近使用、拖动排序、跨页移动与全局快捷键。基于 dsh-quick-input（MIT，cm860712ch-cloud）二次开发，界面与交互层已重写。",
    "en": "A prompt pad beside the DSH composer: open a popover from the stack icon, search or click a saved phrase, and it is inserted at the caret as one undoable edit. Adds hover preview, a recent-used page, drag-to-reorder, cross-page moves and a global hotkey. Fork of dsh-quick-input (MIT, cm860712ch-cloud); the UI layer has been rewritten."
  },
  "npm": null,
  "install": "dsh plugin --profile web add github:oWo1025/dsh-prompt-input",
  "icon": "https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/icon.svg",
  "screenshots": [
    "https://raw.githubusercontent.com/oWo1025/dsh-prompt-input/main/docs/panel.png"
  ]
}
```

要点：

- `category` 用 `ui`（界面增强）。
- **必须写明 fork 关系**，现有条目里已有先例（如 `dsh-free-mode` 写 "Repackaged from …"、`dsh-pua` 的修订版写 "Fork of …"）。
- `install` 与 `name` 要对上你要发布的那份。
- `capabilities` 由站点自动检测，不用自己填。

## 四、上架步骤

1. Fork [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)。
2. 按它仓库说明的格式，把你的条目加进去（一个条目一条）——**不要往 dsh-market 那个市场仓库提条目**，
   它的 README 明确写了"这个仓库是市场应用本身，不是插件目录"。
3. 提 PR，说明改了哪个条目。
4. 通常一天内站点与市场都会收录；市场只会安装这个列表里的来源。

## 五、给上游提 PR

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

## 六、发布到 npm（可选）

```bash
npx tsc -v                 # 本项目无构建步骤，纯 JS
npm whoami                 # 确认登录
npm publish --access public
```

发布前把 `package.json` 的 `files` 收紧（当前已排除 `dev/`、`docs/`），并确认 `name` 已改。
