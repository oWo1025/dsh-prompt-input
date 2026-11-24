# -*- coding: utf-8 -*-
"""P0 第二步：替换面板组件（气泡 + 搜索 + 键盘），并更新版本号与客户端依赖顺序。"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
CLIENT = os.path.join(DEV, "client.js")

src = open(CLIENT, encoding="utf-8").read()

PANEL = '''    function QuickPanel(props) {
      useStore()
      const t = translator(props)
      const sessionId = bridge.sessionId
      const open = sessionId !== null && sessionId !== undefined && isOpen(sessionId)
      const [anchor, setAnchor] = React.useState(null)
      const rootRef = React.useRef(null)

      // 打开时量锚点；窗口变了、或者草稿长高把 ⊞ 顶走了，跟着重量。
      React.useEffect(() => {
        if (!open) return undefined
        const measure = () => {
          const node = bridge.node
          if (!node || typeof node.getBoundingClientRect !== 'function') return
          const rect = node.getBoundingClientRect()
          if (!rect || rect.width <= 0) return
          setAnchor((previous) => {
            if (
              previous &&
              previous.left === rect.left &&
              previous.top === rect.top &&
              previous.right === rect.right &&
              previous.bottom === rect.bottom
            ) {
              return previous
            }
            return { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom }
          })
        }
        measure()
        const disposers = []
        if (typeof window.addEventListener === 'function') {
          window.addEventListener('resize', measure)
          disposers.push(() => window.removeEventListener('resize', measure))
        }
        // ⊞ 会被宿主布局改动（侧栏开合、草稿长高）挪走，低频跟一下就够了。
        const timer = setInterval(measure, 500)
        disposers.push(() => clearInterval(timer))
        return () => {
          for (const dispose of disposers) {
            try {
              dispose()
            } catch {
              /* 清理失败不影响界面 */
            }
          }
        }
      }, [open])

      // 点面板外关闭：面板外 + ⊞ 外才算外（和 DSH 菜单的判定一致）。
      React.useEffect(() => {
        if (!open) return undefined
        const onDown = (event) => {
          const root = rootRef.current
          const target = event.target
          if (root && typeof root.contains === 'function' && root.contains(target)) return
          if (bridge.node && typeof bridge.node.contains === 'function' && bridge.node.contains(target)) return
          closePanel(sessionId)
        }
        document.addEventListener('mousedown', onDown, true)
        return () => document.removeEventListener('mousedown', onDown, true)
      }, [open, sessionId])

      // Esc：只在焦点真的落在面板里时接管，绝不抢输入框的 Esc。
      React.useEffect(() => {
        if (!open) return undefined
        const onKey = (event) => {
          if (event.key !== 'Escape') return
          const root = rootRef.current
          if (!root || !root.contains(document.activeElement)) return
          event.preventDefault()
          event.stopPropagation()
          closePanel(sessionId)
        }
        document.addEventListener('keydown', onKey, true)
        return () => document.removeEventListener('keydown', onKey, true)
      }, [open, sessionId])

      if (!open) return null
      if (anchor === null) return null

      const pages = store.doc.pages
      const pageIndex =
        pages.length === 0 ? 0 : Math.min(Math.max(store.page.get(sessionId) ?? 0, 0), pages.length - 1)
      const page = pages[pageIndex]
      const editing = store.editing.get(sessionId) ?? null
      const editMode = store.editMode.get(sessionId) === true
      const flash = store.flash.get(sessionId) ?? null
      const search = readSearch(sessionId)
      const results = searchPages(pages, search.query) ?? []
      const active = Math.min(Math.max(search.active, 0), Math.max(results.length - 1, 0))

      const insert = (cell) => {
        const result = insertIntoDraft(bridge.inputActions, cell.text, bridge.phase)
        if (result.ok === true) setFlash(sessionId, 'ok', t('inserted', { text: toLabel('', cell.text) }))
        else setFlash(sessionId, 'err', result.reason)
      }

      const openEditor = (index) => {
        store.page.set(sessionId, pageIndex)
        store.editing.set(sessionId, { page: pageIndex, cell: index })
        store.emit()
      }

      const addPage = async () => {
        if (pages.length >= MAX_PAGES) return
        const next = clonePages()
        next.push({
          title: t('pageNumber', { index: pages.length + 1 }),
          cells: new Array(CELLS_PER_PAGE).fill(null),
        })
        try {
          await commit(next)
          store.page.set(sessionId, next.length - 1)
          store.editMode.set(sessionId, true)
          store.editing.set(sessionId, { page: next.length - 1, cell: 0 })
          setFlash(sessionId, 'ok', t('newPageReady'))
        } catch (failure) {
          setFlash(sessionId, 'err', messageOf(failure))
        }
      }

      /** 网格内的方向键：在卡片之间移动焦点（3 列）。 */
      const onGridKey = (event) => {
        const key = event.key
        if (key !== 'ArrowLeft' && key !== 'ArrowRight' && key !== 'ArrowUp' && key !== 'ArrowDown') return
        const buttons = Array.from(event.currentTarget.querySelectorAll('button'))
        const current = buttons.indexOf(document.activeElement)
        if (current < 0) return
        const delta = key === 'ArrowRight' ? 1 : key === 'ArrowLeft' ? -1 : key === 'ArrowDown' ? 3 : -3
        const next = current + delta
        if (next < 0 || next >= buttons.length) return
        event.preventDefault()
        buttons[next].focus()
      }

      const head = h(
        'div',
        { className: 'dsq-head' },
        h('input', {
          className: 'dsq-search',
          type: 'search',
          value: search.query,
          placeholder: t('searchPlaceholder'),
          'aria-label': t('searchPlaceholder'),
          onChange: (event) => {
            writeSearch(sessionId, { query: event.target.value, active: 0 })
            store.emit()
          },
          onKeyDown: (event) => {
            if (event.key === 'ArrowDown') {
              event.preventDefault()
              writeSearch(sessionId, { active: Math.min(active + 1, Math.max(results.length - 1, 0)) })
              store.emit()
            } else if (event.key === 'ArrowUp') {
              event.preventDefault()
              writeSearch(sessionId, { active: Math.max(active - 1, 0) })
              store.emit()
            } else if (event.key === 'Enter') {
              event.preventDefault()
              const hit = results[active]
              if (hit) insert(hit)
            } else if (event.key === 'Escape') {
              event.preventDefault()
              if (search.query !== '') {
                writeSearch(sessionId, { query: '', active: 0 })
                store.emit()
              } else {
                closePanel(sessionId)
              }
            }
          },
        }),
        h(
          'button',
          {
            type: 'button',
            className: 'dsq-x',
            title: t('collapse'),
            'aria-label': t('collapse'),
            onMouseDown: keepFocus,
            onClick: () => closePanel(sessionId),
          },
          '×',
        ),
      )

      const tabs = h(
        'div',
        { className: 'dsq-tabs', role: 'tablist' },
        pages.map((item, index) =>
          h(
            'button',
            {
              key: `tab-${index}`,
              type: 'button',
              role: 'tab',
              'aria-selected': index === pageIndex ? 'true' : 'false',
              className: index === pageIndex ? 'dsq-tab dsq-tab-on' : 'dsq-tab',
              title: t('pageHint', { title: item.title, index: index + 1, total: Math.max(pages.length, 1) }),
              onMouseDown: keepFocus,
              onClick: () => {
                store.page.set(sessionId, index)
                store.editing.set(sessionId, null)
                store.emit()
              },
            },
            item.title,
          ),
        ),
      )

      const grid =
        page === undefined
          ? null
          : h(
              'div',
              { className: 'dsq-grid3', role: 'group', 'aria-label': t('panelAria'), onKeyDown: onGridKey },
              page.cells.map((cell, index) => {
                if (!cell) {
                  return editMode
                    ? h(
                        'button',
                        {
                          key: `c-${index}`,
                          type: 'button',
                          className: 'dsq-card dsq-card-empty',
                          title: t('emptyCell'),
                          onMouseDown: keepFocus,
                          onClick: () => openEditor(index),
                        },
                        '＋',
                      )
                    : null
                }
                return h(
                  'button',
                  {
                    key: `c-${index}`,
                    type: 'button',
                    className: 'dsq-card',
                    title: cell.text,
                    onMouseDown: keepFocus,
                    onClick: () => (editMode ? openEditor(index) : insert(cell)),
                    onContextMenu: (event) => {
                      if (event && typeof event.preventDefault === 'function') event.preventDefault()
                      openEditor(index)
                    },
                  },
                  h('span', { className: 'dsq-card-label' }, cell.label),
                  editMode ? h('span', { className: 'dsq-card-sub' }, t('editCellShort')) : null,
                )
              }),
            )

      const list = h(
        'div',
        { className: 'dsq-results', role: 'listbox', 'aria-label': t('searchPlaceholder') },
        results.length === 0
          ? h('div', { className: 'dsq-muted', style: { padding: '10px 8px' } }, t('noResults', { q: search.query }))
          : results.map((item, index) =>
              h(
                'button',
                {
                  key: `r-${item.pageIndex}-${item.cellIndex}`,
                  type: 'button',
                  role: 'option',
                  'aria-selected': index === active ? 'true' : 'false',
                  className: index === active ? 'dsq-item dsq-item-on' : 'dsq-item',
                  title: item.text,
                  onMouseDown: keepFocus,
                  onClick: () => insert(item),
                  onMouseEnter: () => {
                    if (index === active) return
                    writeSearch(sessionId, { active: index })
                    store.emit()
                  },
                },
                h('span', { className: 'dsq-item-label' }, item.label),
                h('span', { className: 'dsq-item-snippet' }, snippet(item.text)),
                h('span', { className: 'dsq-item-page' }, item.page),
              ),
            ),
      )

      let body = null
      if (store.doc.status === 'loading' && pages.length === 0) {
        body = h('div', { className: 'dsq-muted', style: { padding: '12px 8px' } }, t('loading'))
      } else if (store.doc.status === 'error' && pages.length === 0) {
        body = h(
          'div',
          { style: { display: 'flex', flexDirection: 'column', gap: 6, padding: '6px 4px' } },
          h('div', { className: 'dsq-err' }, t('readFailed', { message: store.doc.error })),
          h(
            'button',
            { type: 'button', className: 'dsq-action', onMouseDown: keepFocus, onClick: () => ensureDoc(true) },
            t('retry'),
          ),
        )
      } else if (editing !== null) {
        body = h(
          React.Fragment,
          null,
          h(PageRow, { key: `page-${pageIndex}`, sessionId, page: pageIndex, t }),
          h(CellEditor, {
            key: `cell-${pageIndex}-${editing.cell}`,
            sessionId,
            page: pageIndex,
            cell: editing.cell,
            t,
          }),
        )
      } else if (search.query !== '') {
        body = list
      } else {
        body = grid
      }

      const foot = h(
        'div',
        { className: 'dsq-foot' },
        h(
          'span',
          { className: 'dsq-foot-grow' },
          flash
            ? h('span', { className: flash.kind === 'ok' ? 'dsq-ok' : 'dsq-err' }, flash.text)
            : search.query !== ''
              ? t('searchCount', { n: results.length })
              : page
                ? t('pageHint', { title: page.title, index: pageIndex + 1, total: Math.max(pages.length, 1) })
                : '',
        ),
        editMode && pages.length < MAX_PAGES
          ? h(
              'button',
              { type: 'button', className: 'dsq-mini', title: t('addPage'), onMouseDown: keepFocus, onClick: addPage },
              t('addPageShort'),
            )
          : null,
        h(
          'button',
          {
            type: 'button',
            className: 'dsq-mini',
            title: editMode ? t('finishEdit') : t('editPresets'),
            onMouseDown: keepFocus,
            onClick: () => {
              if (pages.length === 0) return
              store.editing.set(sessionId, null)
              store.editMode.set(sessionId, editMode !== true)
              store.emit()
            },
          },
          editMode ? t('done') : '✎',
        ),
      )

      return h(
        React.Fragment,
        null,
        h('style', null, CSS),
        h(
          'div',
          {
            ref: rootRef,
            className: 'dsq-pop',
            style: popoverStyle(anchor),
            role: 'dialog',
            'aria-modal': 'false',
            'aria-label': t('panelAria'),
          },
          head,
          tabs,
          h(
            'div',
            {
              style: {
                flex: '1 1 auto',
                minHeight: 0,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
              },
            },
            body,
          ),
          foot,
        ),
      )
    }

'''

start = "    function QuickPanel(props) {"
end = "    // ------------------------------------------------------------ 兜底"
assert src.count(start) == 1 and src.count(end) == 1
a, b = src.index(start), src.index(end)
assert a < b
src = src[:a] + PANEL + src[b:]

# 客户端构建号：让 /quick-input/health 能区分跑的是哪一份
src = src.replace("const CLIENT_BUILD = '0.1.0+build8'", "const CLIENT_BUILD = '0.2.0+build1'")
assert "0.2.0+build1" in src

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("panel replaced, size =", len(src))

# ---------------------------------------------------------------- package.json
PKG = os.path.join(DEV, "package.json")
pkg = json.load(open(PKG, encoding="utf-8"))
pkg["version"] = "0.2.0"
pkg["description"] = (
    "应声 · 快捷输入：点开输入框左侧的 ⊞，从气泡里搜索/点选预设短语并插到光标处。"
    "Popover quick-phrase pad with search: open from ⊞ beside the composer, click a card to insert at the caret."
)
inject = pkg.get("dsh", {}).get("client", {}).get("inject", [])
for extra in ("@deepseek-ai/dsh-client-ui-layout",):
    if extra not in inject:
        inject.append(extra)
pkg["dsh"]["client"]["inject"] = inject
json.dump(pkg, open(PKG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(PKG, "a", encoding="utf-8").write("\n")
print("package.json ->", pkg["version"], inject)

# ---------------------------------------------------------------- index.js 版本号
IDX = os.path.join(DEV, "index.js")
idx = open(IDX, encoding="utf-8").read()
idx = idx.replace("const VERSION = '0.1.0'", "const VERSION = '0.2.0'")
open(IDX, "w", encoding="utf-8", newline="\n").write(idx)
print("index.js version:", "0.2.0" in idx)
