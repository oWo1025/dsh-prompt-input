# -*- coding: utf-8 -*-
"""0.2.4：最近使用置顶（虚拟「最近」页，最多 8 条）。"""
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


# ---------------------------------------------------------------- 1. store 加一列
sub("""      flash: new Map(),
      doc: { status: 'idle', pages: [], error: '' },""",
    """      flash: new Map(),
      /** 是否停在虚拟的「最近」页。 */
      recentView: new Map(),
      doc: { status: 'idle', pages: [], error: '' },""",
    "store")

# ---------------------------------------------------------------- 2. 最近使用的读写
sub("""    function writeSearch(sessionId, patch) {
      searchState.set(sessionId, { ...readSearch(sessionId), ...patch })
    }""",
    """    function writeSearch(sessionId, patch) {
      searchState.set(sessionId, { ...readSearch(sessionId), ...patch })
    }

    // ------------------------------------------------------------ 最近使用

    /** 点过的 prompt 置顶，最多 8 条，按正文去重（同一条不会重复占位）。 */
    const RECENT_KEY = 'quick-input.recent.v1'
    const RECENT_MAX = 8

    function readRecent() {
      try {
        const raw = window.localStorage ? window.localStorage.getItem(RECENT_KEY) : null
        if (!raw) return []
        const list = JSON.parse(raw)
        if (!Array.isArray(list)) return []
        return list
          .filter((item) => item && typeof item.text === 'string' && typeof item.label === 'string')
          .slice(0, RECENT_MAX)
      } catch {
        return []
      }
    }

    function pushRecent(item) {
      if (!item || typeof item.text !== 'string' || item.text === '') return
      try {
        if (!window.localStorage) return
        const list = readRecent().filter((entry) => entry.text !== item.text)
        list.unshift({ label: item.label || '', text: item.text, page: item.page || '' })
        window.localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, RECENT_MAX)))
      } catch {
        /* 存不了就算了，不影响插入 */
      }
    }""",
    "recent-helpers")

# ---------------------------------------------------------------- 3. 插入时记账
sub("""      const insert = (cell) => {
        stopPreview()
        const result = insertIntoDraft(bridge.inputActions, cell.text, bridge.phase)
        if (result.ok === true) setFlash(sessionId, 'ok', t('inserted', { text: toLabel('', cell.text) }))
        else setFlash(sessionId, 'err', result.reason)
      }""",
    """      const insert = (cell) => {
        stopPreview()
        const result = insertIntoDraft(bridge.inputActions, cell.text, bridge.phase)
        if (result.ok === true) {
          pushRecent({ label: cell.label, text: cell.text, page: cell.page })
          setFlash(sessionId, 'ok', t('inserted', { text: toLabel('', cell.text) }))
        } else {
          setFlash(sessionId, 'err', result.reason)
        }
      }""",
    "insert")

# ---------------------------------------------------------------- 4. 视图状态
sub("""      const editMode = store.editMode.get(sessionId) === true""",
    """      const editMode = store.editMode.get(sessionId) === true
      const recent = readRecent()
      const showRecent = store.recentView.get(sessionId) === true && recent.length > 0""",
    "view-state")

# ---------------------------------------------------------------- 5. 「最近」页不能拖格子
sub("""      const beginCellDrag = (event, index) => {
        if (!editMode || !event || event.button !== 0) return""",
    """      const beginCellDrag = (event, index) => {
        if (!editMode || showRecent || !event || event.button !== 0) return""",
    "drag-guard")

# ---------------------------------------------------------------- 6. 页签：最前面加「最近」
sub("""        { className: 'dsq-tabs', role: 'tablist' },
        pages.map((item, index) =>""",
    """        { className: 'dsq-tabs', role: 'tablist' },
        recent.length > 0
          ? h(
              'button',
              {
                key: 'tab-recent',
                type: 'button',
                role: 'tab',
                'aria-selected': showRecent ? 'true' : 'false',
                className: showRecent ? 'dsq-tab dsq-tab-on' : 'dsq-tab',
                title: t('recentHint'),
                onMouseDown: keepFocus,
                onClick: () => {
                  store.recentView.set(sessionId, true)
                  store.editMode.set(sessionId, false)
                  store.editing.set(sessionId, null)
                  store.emit()
                },
              },
              t('recentTab'),
            )
          : null,
        pages.map((item, index) =>""",
    "tabs-recent")

sub("""              'aria-selected': index === pageIndex ? 'true' : 'false',
              'data-page': index,
              className:
                (index === pageIndex ? 'dsq-tab dsq-tab-on' : 'dsq-tab') +""",
    """              'aria-selected': !showRecent && index === pageIndex ? 'true' : 'false',
              'data-page': index,
              className:
                (!showRecent && index === pageIndex ? 'dsq-tab dsq-tab-on' : 'dsq-tab') +""",
    "tab-active")

sub("""              onClick: () => {
                store.page.set(sessionId, index)
                store.editing.set(sessionId, null)
                store.emit()
              },""",
    """              onClick: () => {
                store.recentView.set(sessionId, false)
                store.page.set(sessionId, index)
                store.editing.set(sessionId, null)
                store.emit()
              },""",
    "tab-click")

# ---------------------------------------------------------------- 7. 网格插入带上页名（给最近使用记账）
sub("""                    onClick: () => (editMode ? openEditor(index) : insert(cell)),""",
    """                    onClick: () =>
                      editMode
                        ? openEditor(index)
                        : insert({ label: cell.label, text: cell.text, page: page ? page.title : '' }),""",
    "card-insert")

# ---------------------------------------------------------------- 8. 「最近」网格
sub("""      const list = h(
        'div',
        { className: 'dsq-results', role: 'listbox', 'aria-label': t('searchPlaceholder') },""",
    """      const recentGrid =
        recent.length === 0
          ? null
          : h(
              'div',
              { className: 'dsq-grid3', role: 'group', 'aria-label': t('recentTab') },
              recent.map((item, index) =>
                h(
                  'button',
                  {
                    key: `recent-${index}-${item.text.length}`,
                    type: 'button',
                    className: 'dsq-card',
                    title: item.text,
                    onMouseDown: keepFocus,
                    onMouseEnter: (event) => hoverEnter(event, item),
                    onMouseLeave: hoverLeave,
                    onClick: () => insert(item),
                  },
                  h('span', { className: 'dsq-card-label' }, item.label || toLabel('', item.text)),
                  h('span', { className: 'dsq-card-sub' }, item.page || ''),
                ),
              ),
            )

      const list = h(
        'div',
        { className: 'dsq-results', role: 'listbox', 'aria-label': t('searchPlaceholder') },""",
    "recent-grid")

# ---------------------------------------------------------------- 9. 渲染分支
sub("""      } else if (search.query !== '') {
        body = list
      } else {
        body = grid
      }""",
    """      } else if (search.query !== '') {
        body = list
      } else if (showRecent) {
        body = recentGrid
      } else {
        body = grid
      }""",
    "body")

# ---------------------------------------------------------------- 10. 字典
sub("""        movedCell: '已移动',""",
    """        movedCell: '已移动',
        recentTab: '最近',
        recentHint: '最近点过的 prompt（自动保留 8 条，不可编辑）',""",
    "dict-zh")

sub("""        movedCell: 'Moved',""",
    """        movedCell: 'Moved',
        recentTab: 'Recent',
        recentHint: 'Recently inserted prompts (last 8, read-only)',""",
    "dict-en")

# ---------------------------------------------------------------- 11. 版本
sub("const CLIENT_BUILD = '0.2.3+build1'", "const CLIENT_BUILD = '0.2.4+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.3'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.3'", "const VERSION = '0.2.4'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.4"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

print("ok ->", pkg["version"], "| size", len(src))
