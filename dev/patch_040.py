# -*- coding: utf-8 -*-
"""0.4.0：与上游隔离命名空间（行 id / 路由 / 预设文件 / localStorage / 槽位 / 快捷键），带一次性迁移。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\dsh-prompt-input"


def edit(name, pairs):
    path = os.path.join(DEV, name)
    text = open(path, encoding="utf-8").read()
    for old, new, expect in pairs:
        got = text.count(old)
        assert got == expect, f"{name}: {old[:60]!r} expected {expect} got {got}"
        text = text.replace(old, new)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("ok", name)


# ============================================================ index.js
edit("index.js", [
    ("import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'",
     "import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'", 1),
    (""" * 快捷输入 —— 宿主半区。
 *
 * 职责只有两件：
 *   1. 持有预设（$DSH_HOME/quick-input/presets.json），首次使用时写入默认种子；
 *   2. 用 ctx.webServer 注册 /quick-input/* 路由，给浏览器半区读、存预设。""",
     """ * Prompt 面板 —— 宿主半区。
 *
 * 职责只有两件：
 *   1. 持有预设（$DSH_HOME/dsh-prompt-input/presets.json），首次使用时写入默认种子；
 *   2. 用 ctx.webServer 注册 /dsh-prompt-input/* 路由，给浏览器半区读、存预设。
 *
 * 命名空间是独立的一套：路由、预设目录、槽位 id、localStorage 键都不与上游 dsh-quick-input 共用，
 * 两个插件同时装也不会互相踩。旧路径的数据在启动时一次性迁移。""", 1),
    ("export const name = 'quick-input'", "export const name = 'dsh-prompt-input'", 1),
    ("const VERSION = '0.3.4'", "const VERSION = '0.4.0'", 1),
    ("const ROUTE_PATH = '/quick-input'", "const ROUTE_PATH = '/dsh-prompt-input'", 1),
    ("ctx.logger('quick-input')", "ctx.logger('dsh-prompt-input')", 1),
    ("""/** 预设文件位置：$DSH_HOME/quick-input/presets.json。 */
function storeFile() {
  const home = process.env.DSH_HOME || join(homedir(), '.dsh')
  return join(home, 'quick-input', 'presets.json')
}""",
     """/** 预设文件位置：$DSH_HOME/dsh-prompt-input/presets.json。 */
function storeFile() {
  const home = process.env.DSH_HOME || join(homedir(), '.dsh')
  return join(home, 'dsh-prompt-input', 'presets.json')
}

/** 0.3 及以前的位置（上游也用这个路径），仅用于一次性迁移。 */
function legacyStoreFile() {
  const home = process.env.DSH_HOME || join(homedir(), '.dsh')
  return join(home, 'quick-input', 'presets.json')
}

/**
 * 把旧路径的预设复制到新路径（只在新文件不存在时做一次，旧文件保留不删）。
 * 迁移失败不阻塞启动：读不到就用种子，用户仍是可用状态。
 */
function migrateStore(log) {
  const next = storeFile()
  const legacy = legacyStoreFile()
  try {
    if (existsSync(next) || !existsSync(legacy)) return
    const normalized = normalizePresets(JSON.parse(readFileSync(legacy, 'utf8')))
    if (normalized.pages.length === 0) return
    mkdirSync(dirname(next), { recursive: true })
    writeFileSync(next, `${JSON.stringify(normalized, null, 2)}\\n`, 'utf8')
    log.info?.(`[dsh-prompt-input] 已迁移旧预设：${legacy} → ${next}（旧文件保留）`)
  } catch (error) {
    log.warn?.(
      '[dsh-prompt-input] 迁移旧预设失败，将使用默认种子：',
      error instanceof Error ? error.message : String(error),
    )
  }
}""", 1),
    ("  const seed = seedFromConfig(rawConfig)",
     "  const seed = seedFromConfig(rawConfig)\n\n  // 先迁移旧路径，后面的读取才有东西可用。\n  migrateStore(log)", 1),
    ("  /** GET /quick-input/presets 读；POST 存。 */", "  /** GET /dsh-prompt-input/presets 读；POST 存。 */", 1),
    ("'quick-input.route'", "'dsh-prompt-input.route'", 1),
    ("[quick-input] 预设文件里没有有效页面，改用种子重建", "[dsh-prompt-input] 预设文件里没有有效页面，改用种子重建", 1),
    ("[quick-input] 读预设失败，改用种子：", "[dsh-prompt-input] 读预设失败，改用种子：", 1),
    ("[quick-input] 种子落盘失败（不影响本次使用）：", "[dsh-prompt-input] 种子落盘失败（不影响本次使用）：", 1),
    ("[quick-input] 浏览器半区报到：", "[dsh-prompt-input] 浏览器半区报到：", 1),
    ("[quick-input] 请求处理失败：", "[dsh-prompt-input] 请求处理失败：", 1),
    ("[quick-input] 预设文件：", "[dsh-prompt-input] 预设文件：", 1),
])

# ============================================================ client.js
edit("client.js", [
    ("    const API = '/quick-input'\n\n    /** 客户端构建号：页面加载时回报给宿主，`GET /quick-input/health` 里能看到跑的是哪一份。 */",
     "    /** 宿主路由基址：0.4 起改名；首个元素是当前名字，第二个是旧名字（宿主未重启时回退）。 */\n"
     "    const API_CANDIDATES = ['/dsh-prompt-input', '/quick-input']\n\n"
     "    /** 客户端构建号：页面加载时回报给宿主，`GET /dsh-prompt-input/health` 里能看到跑的是哪一份。 */", 1),
    ("    const NS = 'quick-input'", "    const NS = 'dsh-prompt-input'", 1),
    ("    const RECENT_KEY = 'quick-input.recent.v1'",
     "    const RECENT_KEY = 'dsh-prompt-input.recent.v1'\n    /** 0.3 及以前的键名，读时兜底、写时不再用它。 */\n    const LEGACY_RECENT_KEY = 'quick-input.recent.v1'", 1),
    ("        const raw = window.localStorage ? window.localStorage.getItem(RECENT_KEY) : null",
     "        const raw = window.localStorage\n"
     "          ? window.localStorage.getItem(RECENT_KEY) ?? window.localStorage.getItem(LEGACY_RECENT_KEY)\n"
     "          : null", 1),
    ("    const POS_KEY = 'quick-input.pos.v1'",
     "    const POS_KEY = 'dsh-prompt-input.pos.v1'\n    /** 0.3 及以前的键名，读时兜底。 */\n    const LEGACY_POS_KEY = 'quick-input.pos.v1'", 1),
    ("        const raw = window.localStorage ? window.localStorage.getItem(POS_KEY) : null",
     "        const raw = window.localStorage\n"
     "          ? window.localStorage.getItem(POS_KEY) ?? window.localStorage.getItem(LEGACY_POS_KEY)\n"
     "          : null", 1),
    ("        const raw = window.localStorage.getItem(POS_KEY)",
     "        const raw =\n"
     "          window.localStorage.getItem(POS_KEY) ?? window.localStorage.getItem(LEGACY_POS_KEY)", 1),
    ("    /** 编辑一格：名称 + 内容；保存走 POST /quick-input/presets。 */",
     "    /** 编辑一格：名称 + 内容；保存走 POST /dsh-prompt-input/presets。 */", 1),
    # 请求层：旧宿主（未重启）自动回退
    ("""    async function request(path, options) {
      const response = await fetch(`${API}${path}`, options)
      let body = null""",
     """    /** 当前生效的路由基址；首次请求失败会自动切到旧名字。 */
    let apiBase = API_CANDIDATES[0]

    async function request(path, options) {
      let response
      try {
        response = await fetch(`${apiBase}${path}`, options)
      } catch (error) {
        if (apiBase !== API_CANDIDATES[1]) {
          apiBase = API_CANDIDATES[1]
          response = await fetch(`${apiBase}${path}`, options)
        } else {
          throw error
        }
      }
      // 宿主还没重启时新路由是 404，退回旧路由（旧版宿主仍只认它）。
      if (response.status === 404 && apiBase === API_CANDIDATES[0]) {
        const retry = await fetch(`${API_CANDIDATES[1]}${path}`, options)
        if (retry.ok) {
          apiBase = API_CANDIDATES[1]
          response = retry
        }
      }
      let body = null""", 1),
    ("        const call = fetch(`${API}/hello`, {", "        const call = fetch(`${apiBase}/hello`, {", 1),
    ("console.error('[quick-input] 界面渲染失败：', error)", "console.error('[dsh-prompt-input] 界面渲染失败：', error)", 1),
    ("console.warn('[quick-input] 快捷键注册失败：', error)", "console.warn('[dsh-prompt-input] 快捷键注册失败：', error)", 1),
    ("    /** 向宿主报到：这样 `GET /quick-input/health` 能证明页面正在跑哪一份客户端代码。 */",
     "    /** 向宿主报到：这样 `GET /dsh-prompt-input/health` 能证明页面正在跑哪一份客户端代码。 */", 1),
    ("靠这个在 `/quick-input/health` 里读出来", "靠这个在 `/dsh-prompt-input/health` 里读出来", 1),
    ("id: 'quick-input-toggle'", "id: 'dsh-prompt-input-toggle'", 1),
    ("id: 'quick-input-panel'", "id: 'dsh-prompt-input-panel'", 1),
    ("id: 'quick-input.toggle'", "id: 'dsh-prompt-input.toggle'", 1),
    ("const CLIENT_BUILD = '0.3.4+build1'", "const CLIENT_BUILD = '0.4.0+build1'", 1),
])

# ============================================================ 清单
edit("cordis.patch.yml", [
    ("    - id: quick-input", "    - id: prompt-input", 1),
    ("$DSH_HOME/quick-input/presets.json", "$DSH_HOME/dsh-prompt-input/presets.json", 1),
])

P = os.path.join(DEV, "package.json")
pkg = json.load(open(P, encoding="utf-8"))
pkg["version"] = "0.4.0"
json.dump(pkg, open(P, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(P, "a", encoding="utf-8").write("\n")
print("ok package.json ->", pkg["version"])

CL = os.path.join(DEV, "CHANGELOG.md")
t = open(CL, encoding="utf-8").read()
head = "# Changelog\n\n"
if "0.4.0 —" not in t:
    t = head + """## 0.4.0 — 与上游隔离命名空间（可共存）

0.3 之前虽然改了包名，但内部标识仍沿用上游的一套。有人同时装上游 `dsh-quick-input` 时会出现四种撞车：

| 撞的是什么 | 之前 | 现在 |
|---|---|---|
| cordis 行 id | `quick-input` | `prompt-input` |
| HTTP 路由 | `/quick-input/*` | `/dsh-prompt-input/*` |
| 预设文件 | `$DSH_HOME/quick-input/presets.json` | `$DSH_HOME/dsh-prompt-input/presets.json` |
| localStorage 键 | `quick-input.pos.v1` / `.recent.v1` | `dsh-prompt-input.*` |
| 槽位 id / 快捷键 id | `quick-input-toggle` / `quick-input.toggle` | `dsh-prompt-input-*` / `dsh-prompt-input.toggle` |

**数据不会丢**：

- 宿主动手前会做一次迁移：新路径不存在、旧路径存在时，把旧预设规范化后复制到新路径，
  **旧文件保留**（想回退随时可以）。
- 浏览器半区读 localStorage 时先读新键、读不到再读旧键，用户的拖动位置和「最近使用」照旧。
- 客户端请求失败或 404 时会自动退到旧路由 `/quick-input`，所以**宿主还没重启的那段时间也能用**。

⚠️ 升级后建议重启一次 DSH：宿主半区（路由与迁移逻辑）不会热更新。

""" + t[len(head):]
    open(CL, "w", encoding="utf-8", newline="\n").write(t)

print("done")
