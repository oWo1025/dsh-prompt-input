# -*- coding: utf-8 -*-
"""0.2.5：页签溢出修复（渐隐 + 左右翻页 + 自动滚动）+ 视觉打磨。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
CLIENT = os.path.join(DEV, "client.js")
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    got = src.count(old)
    assert got == 1, f"[{label}] expected 1 got {got}"
    src = src.replace(old, new)


# ---------------------------------------------------------------- 1. 样式
sub("""/* 拖拽：标题行被搜索框占满，所以左上角单独给一个六点把手 */""",
    """/* 半径约定：气泡 16 / 卡片 10 / 输入框与按钮 8 / 页签胶囊 999（全局只此一套） */

/* 拖拽：标题行被搜索框占满，所以左上角单独给一个六点把手 */""",
    "css-note")

sub(""".dsq-btn{box-sizing:border-box;width:28px;height:28px;flex:none;display:grid;place-items:center;padding:0;border:0;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);cursor:pointer;transition:background-color .12s ease,color .12s ease}""",
    """.dsq-btn{box-sizing:border-box;width:28px;height:28px;flex:none;display:grid;place-items:center;padding:0;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:var(--dsw-alias-label-secondary,#667085);cursor:pointer;transition:background-color .12s ease,color .12s ease,transform .12s ease}
.dsq-btn:active{transform:scale(.94)}""",
    "css-btn")

sub(""".dsq-card{box-sizing:border-box;display:flex;flex-direction:column;gap:1px;align-items:flex-start;justify-content:flex-start;padding:7px 8px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));border-radius:var(--dsw-radius-md,10px);background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:16px;text-align:left;cursor:pointer;overflow:hidden;transition:background-color .12s ease,border-color .12s ease,transform .1s ease}
.dsq-card:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));border-color:var(--dsw-alias-border-l2,rgba(0,0,0,.16))}
.dsq-card:active{transform:scale(.985)}""",
    """.dsq-card{box-sizing:border-box;display:flex;flex-direction:column;gap:1px;align-items:flex-start;justify-content:flex-start;padding:7px 8px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));border-radius:var(--dsw-radius-md,10px);background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:16px;text-align:left;cursor:pointer;overflow:hidden;transition:background-color .12s ease,border-color .12s ease,box-shadow .16s ease,transform .12s ease}
.dsq-card:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));border-color:color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 24%,var(--dsw-alias-border-l2,rgba(0,0,0,.16)));box-shadow:0 6px 16px -10px color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 55%,transparent);transform:translateY(-1px)}
.dsq-card:active{transform:translateY(0) scale(.99);box-shadow:none}""",
    "css-card")

sub(""".dsq-card-label{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;width:100%;overflow-wrap:anywhere;font-weight:500}""",
    """.dsq-card-label{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;width:100%;overflow-wrap:anywhere;font-weight:600;letter-spacing:-.01em}""",
    "css-label")

sub(""".dsq-search::placeholder{color:var(--dsw-alias-label-caption,#98a2b3)}""",
    """.dsq-search::placeholder{color:var(--dsw-alias-label-secondary,#667085);opacity:.9}""",
    "css-placeholder")

sub(""".dsq-search:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));background:var(--dsw-alias-bg-layer-2,#fff)}""",
    """.dsq-search:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));background:var(--dsw-alias-bg-layer-2,#fff);box-shadow:0 0 0 3px color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 14%,transparent)}""",
    "css-focus")

sub(""".dsq-tab{box-sizing:border-box;flex:none;height:24px;padding:0 8px;border:1px solid transparent;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-family:inherit;font-size:11.5px;line-height:22px;cursor:pointer;white-space:nowrap;transition:background-color .12s ease,color .12s ease,border-color .12s ease}""",
    """.dsq-tab{box-sizing:border-box;flex:none;height:24px;padding:0 7px;border:1px solid transparent;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-family:inherit;font-size:11px;line-height:22px;cursor:pointer;white-space:nowrap;transition:background-color .12s ease,color .12s ease,border-color .12s ease,transform .12s ease}
.dsq-tab:active{transform:scale(.96)}""",
    "css-tab")

sub(""".dsq-preview-foot{margin-top:7px;font-size:10px;line-height:14px;color:var(--dsw-alias-label-caption,#98a2b3)}
`""",
    """.dsq-preview-foot{margin-top:7px;font-size:10px;line-height:14px;color:var(--dsw-alias-label-caption,#98a2b3)}

/* 页签溢出：两端渐隐，提示"还有更多" */
.dsq-tabs-scroll{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%)}

/* 空页：给一个可执行的空状态，而不是一片空白 */
.dsq-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;height:168px;text-align:center;color:var(--dsw-alias-label-secondary,#667085);font-size:12px;line-height:18px}
.dsq-empty-title{font-weight:600;color:var(--dsw-alias-label-primary,#1f2328)}
`""",
    "css-empty")

# ---------------------------------------------------------------- 2. 状态与 ref
sub("""      const timers = React.useRef({ show: 0, hide: 0, last: 0 })
      const rootRef = React.useRef(null)""",
    """      const timers = React.useRef({ show: 0, hide: 0, last: 0 })
      const rootRef = React.useRef(null)
      const tabsRef = React.useRef(null)
      const [tabsScrollable, setTabsScrollable] = React.useState(false)""",
    "state")

# ---------------------------------------------------------------- 3. 溢出检测 + 自动滚到当前页签
sub("""      // 点面板外关闭：面板外 + ⊞ 外才算外（和 DSH 菜单的判定一致）。""",
    """      // 页签溢出检测：溢出时给左右翻页按钮 + 两端渐隐，否则第 7 页根本看不到。
      React.useEffect(() => {
        if (!open) return undefined
        const measure = () => {
          const node = tabsRef.current
          if (!node) return
          const overflow = node.scrollWidth > node.clientWidth + 1
          setTabsScrollable((previous) => (previous === overflow ? previous : overflow))
        }
        measure()
        const disposers = []
        if (typeof window.ResizeObserver === 'function' && tabsRef.current) {
          try {
            const observer = new window.ResizeObserver(measure)
            observer.observe(tabsRef.current)
            disposers.push(() => observer.disconnect())
          } catch {
            /* 观察不了就靠定时器 */
          }
        }
        const timer = setInterval(measure, 700)
        disposers.push(() => clearInterval(timer))
        return () => {
          for (const dispose of disposers) {
            try {
              dispose()
            } catch {
              /* 忽略 */
            }
          }
        }
      }, [open, sessionId, store.doc.pages.length, store.recentView.get(sessionId)])

      // 当前页签始终滚在可视区内（切页 / 新增页 / 点「最近」之后）。
      React.useEffect(() => {
        if (!open) return
        const node = tabsRef.current
        if (!node) return
        const active = node.querySelector('[data-active="true"]')
        if (!active) return
        const left = active.offsetLeft
        const right = left + active.offsetWidth
        if (left < node.scrollLeft) node.scrollLeft = Math.max(0, left - 6)
        else if (right > node.scrollLeft + node.clientWidth) node.scrollLeft = right - node.clientWidth + 6
      }, [open, sessionId, store.page.get(sessionId), store.recentView.get(sessionId), store.doc.pages.length])

      // 点面板外关闭：面板外 + ⊞ 外才算外（和 DSH 菜单的判定一致）。""",
    "effects")

# ---------------------------------------------------------------- 4. 页签：ref / 渐隐 / 键盘左右切页
sub("""      const tabs = h(
        'div',
        { className: 'dsq-tabs', role: 'tablist' },""",
    """      const tabs = h(
        'div',
        {
          ref: tabsRef,
          className: tabsScrollable ? 'dsq-tabs dsq-tabs-scroll' : 'dsq-tabs',
          role: 'tablist',
        },""",
    "tabs-ref")

sub("""                'aria-selected': showRecent ? 'true' : 'false',
                className: showRecent ? 'dsq-tab dsq-tab-on' : 'dsq-tab',""",
    """                'aria-selected': showRecent ? 'true' : 'false',
                'data-active': showRecent ? 'true' : 'false',
                className: showRecent ? 'dsq-tab dsq-tab-on' : 'dsq-tab',""",
    "recent-active")

sub("""              'aria-selected': !showRecent && index === pageIndex ? 'true' : 'false',
              'data-page': index,""",
    """              'aria-selected': !showRecent && index === pageIndex ? 'true' : 'false',
              'data-active': !showRecent && index === pageIndex ? 'true' : 'false',
              'data-page': index,""",
    "page-active")

sub("""              title: t('pageHint', { title: item.title, index: index + 1, total: Math.max(pages.length, 1) }),
              onMouseDown: keepFocus,""",
    """              title: t('pageHint', { title: item.title, index: index + 1, total: Math.max(pages.length, 1) }),
              onMouseDown: keepFocus,
              onKeyDown: (event) => {
                if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return
                const step = event.key === 'ArrowRight' ? 1 : -1
                const next = Math.min(Math.max(index + step, 0), pages.length - 1)
                if (next === index) return
                event.preventDefault()
                store.recentView.set(sessionId, false)
                store.page.set(sessionId, next)
                store.editing.set(sessionId, null)
                store.emit()
              },""",
    "tab-keys")

# ---------------------------------------------------------------- 5. 左右翻页按钮 + 空状态
sub("""      const tabsRow = h(
        'div',
        { className: 'dsq-tabsrow' },
        tabs,""",
    """      const nudgeTabs = (direction) => {
        const node = tabsRef.current
        if (!node) return
        node.scrollLeft += direction * Math.max(80, Math.round(node.clientWidth * 0.6))
      }

      const tabsRow = h(
        'div',
        { className: 'dsq-tabsrow' },
        tabsScrollable
          ? h(
              'button',
              {
                type: 'button',
                className: 'dsq-mini',
                title: t('tabsPrev'),
                'aria-label': t('tabsPrev'),
                onMouseDown: keepFocus,
                onClick: () => nudgeTabs(-1),
              },
              '‹',
            )
          : null,
        tabs,
        tabsScrollable
          ? h(
              'button',
              {
                type: 'button',
                className: 'dsq-mini',
                title: t('tabsNext'),
                'aria-label': t('tabsNext'),
                onMouseDown: keepFocus,
                onClick: () => nudgeTabs(1),
              },
              '›',
            )
          : null,""",
    "tabsrow")

sub("""      } else if (showRecent) {
        body = recentGrid
      } else {
        body = grid
      }""",
    """      } else if (showRecent) {
        body = recentGrid
      } else if (page && page.cells.every((cell) => !cell) && !editMode) {
        body = h(
          'div',
          { className: 'dsq-empty' },
          h('div', { className: 'dsq-empty-title' }, t('emptyPageTitle')),
          h('div', null, t('emptyPageHint')),
        )
      } else {
        body = grid
      }""",
    "empty-state")

# ---------------------------------------------------------------- 6. 入口图标：更实、更有状态反馈
sub("""            x: 1.5 + column * 5,
              y: 1.5 + row * 5,
              width: 3.4,
              height: 3.4,
              rx: 1.1,""",
    """            x: 0.6 + column * 5.5,
              y: 0.6 + row * 5.5,
              width: 4,
              height: 4,
              rx: 1.2,""",
    "icon-dots")

# ---------------------------------------------------------------- 7. 字典
sub("""        recentTab: '最近',""",
    """        recentTab: '最近',
        tabsPrev: '向前翻页签',
        tabsNext: '向后翻页签',
        emptyPageTitle: '这一页还空着',
        emptyPageHint: '点底部的 ✎ 添加第一条',""",
    "dict-zh")

sub("""        recentTab: 'Recent',""",
    """        recentTab: 'Recent',
        tabsPrev: 'Scroll tabs left',
        tabsNext: 'Scroll tabs right',
        emptyPageTitle: 'This page is empty',
        emptyPageHint: 'Click ✎ at the bottom to add one',""",
    "dict-en")

# ---------------------------------------------------------------- 8. 版本
sub("const CLIENT_BUILD = '0.2.4+build1'", "const CLIENT_BUILD = '0.2.5+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.4'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.4'", "const VERSION = '0.2.5'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.5"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

print("ok ->", pkg["version"], "| size", len(src))
