# -*- coding: utf-8 -*-
"""0.2.3-b：编辑态拖拽排序、跨页移动、另存为新格。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = r"E:\dsh\quick-input-dev\client.js"
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    got = src.count(old)
    assert got == 1, f"[{label}] expected 1 got {got}"
    src = src.replace(old, new)


# ---------------------------------------------------------------- 1. 状态
sub("""      const [preview, setPreview] = React.useState(null)""",
    """      const [preview, setPreview] = React.useState(null)
      const [cellDrag, setCellDrag] = React.useState(null)""",
    "state")

# ---------------------------------------------------------------- 2. 拖动逻辑
sub("""      const resetPosition = () => {
        savePos(null)
        setDrag(null)
        setPreview(null)
      }""",
    """      const resetPosition = () => {
        savePos(null)
        setDrag(null)
        setPreview(null)
      }

      // —— 编辑态：把格子拖到别的格子（同页重排）或页签（换页） ——
      const dropTargetAt = (x, y) => {
        try {
          const node = document.elementFromPoint(x, y)
          if (!node || typeof node.closest !== 'function') return null
          const cellNode = node.closest('[data-cell]')
          if (cellNode) return { kind: 'cell', index: Number(cellNode.getAttribute('data-cell')) }
          const pageNode = node.closest('[data-page]')
          if (pageNode) return { kind: 'page', index: Number(pageNode.getAttribute('data-page')) }
          return null
        } catch {
          return null
        }
      }

      const beginCellDrag = (event, index) => {
        if (!editMode || !event || event.button !== 0) return
        const startX = event.clientX
        const startY = event.clientY
        let active = false
        let over = null
        const onMove = (moveEvent) => {
          const dx = moveEvent.clientX - startX
          const dy = moveEvent.clientY - startY
          if (!active && Math.abs(dx) + Math.abs(dy) < 6) return
          active = true
          over = dropTargetAt(moveEvent.clientX, moveEvent.clientY)
          setCellDrag({ from: index, over })
          setPreview(null)
        }
        const onUp = () => {
          document.removeEventListener('pointermove', onMove)
          document.removeEventListener('pointerup', onUp)
          setCellDrag(null)
          if (active && over) applyMove(index, over)
        }
        document.addEventListener('pointermove', onMove)
        document.addEventListener('pointerup', onUp)
      }

      const applyMove = async (fromIndex, target) => {
        const pagesNext = clonePages()
        const source = pagesNext[pageIndex]
        if (!source) return
        const cell = source.cells[fromIndex]
        if (!cell) return
        const destinationIndex = target.kind === 'page' ? target.index : pageIndex
        const destination = pagesNext[destinationIndex]
        if (!destination) return

        if (destinationIndex === pageIndex) {
          if (target.kind === 'cell' && target.index === fromIndex) return
          const list = source.cells.slice()
          list.splice(fromIndex, 1)
          list.push(null)
          list.splice(target.kind === 'cell' ? target.index : list.length - 1, 0, cell)
          list.length = CELLS_PER_PAGE
          source.cells = list
        } else {
          // 跨页只追加到第一个空格子，避免覆盖目标页的已有内容
          const slot = destination.cells.indexOf(null)
          if (slot < 0) {
            setFlash(sessionId, 'err', t('pageFull'))
            return
          }
          const from = source.cells.slice()
          from[fromIndex] = null
          source.cells = from
          const to = destination.cells.slice()
          to[slot] = cell
          to.length = CELLS_PER_PAGE
          destination.cells = to
        }

        try {
          await commit(pagesNext)
          setFlash(sessionId, 'ok', t('movedCell'))
        } catch (failure) {
          setFlash(sessionId, 'err', messageOf(failure))
        }
      }""",
    "drag-logic")

# ---------------------------------------------------------------- 3. 页签：可接收拖放
sub("""              className: index === pageIndex ? 'dsq-tab dsq-tab-on' : 'dsq-tab',
              title: t('pageHint', { title: item.title, index: index + 1, total: Math.max(pages.length, 1) }),""",
    """              'data-page': index,
              className:
                (index === pageIndex ? 'dsq-tab dsq-tab-on' : 'dsq-tab') +
                (cellDrag && cellDrag.over && cellDrag.over.kind === 'page' && cellDrag.over.index === index
                  ? ' dsq-tab-over'
                  : ''),
              title: t('pageHint', { title: item.title, index: index + 1, total: Math.max(pages.length, 1) }),""",
    "tabs")

# ---------------------------------------------------------------- 4. 空格子：可作落点
sub("""                          key: `c-${index}`,
                          type: 'button',
                          className: 'dsq-card dsq-card-empty',
                          title: t('emptyCell'),""",
    """                          key: `c-${index}`,
                          type: 'button',
                          'data-cell': index,
                          className:
                            'dsq-card dsq-card-empty' +
                            (cellDrag && cellDrag.over && cellDrag.over.kind === 'cell' && cellDrag.over.index === index
                              ? ' dsq-card-over'
                              : ''),
                          title: t('emptyCell'),""",
    "empty-card")

# ---------------------------------------------------------------- 5. 有内容的格子：可拖、可作落点
sub("""                    key: `c-${index}`,
                    type: 'button',
                    className: 'dsq-card',
                    title: cell.text,
                    onMouseDown: keepFocus,""",
    """                    key: `c-${index}`,
                    type: 'button',
                    'data-cell': index,
                    className:
                      'dsq-card' +
                      (cellDrag && cellDrag.from === index ? ' dsq-card-drag' : '') +
                      (cellDrag && cellDrag.over && cellDrag.over.kind === 'cell' && cellDrag.over.index === index
                        ? ' dsq-card-over'
                        : ''),
                    title: cell.text,
                    onMouseDown: keepFocus,
                    onPointerDown: (event) => beginCellDrag(event, index),""",
    "card")

# ---------------------------------------------------------------- 6. 另存为新格
sub("""      return h(
        'div',
        { className: 'dsq-actions', style: { flexDirection: 'column', alignItems: 'stretch', gap: 6 } },""",
    """      const saveAsNew = async (value) => {
        if (busy) return
        setBusy(true)
        setError('')
        const pages = clonePages()
        const target = pages[props.page]
        if (!target) {
          setError(t('pageGone'))
          setBusy(false)
          return
        }
        const slot = target.cells.indexOf(null)
        if (slot < 0) {
          setError(t('pageFull'))
          setBusy(false)
          return
        }
        target.cells[slot] = value
        try {
          await commit(pages)
          setFlash(sessionId, 'ok', t('saved'))
          close()
        } catch (failure) {
          setError(messageOf(failure))
        } finally {
          setBusy(false)
        }
      }

      return h(
        'div',
        { className: 'dsq-actions', style: { flexDirection: 'column', alignItems: 'stretch', gap: 6 } },""",
    "saveAsNew-fn")

sub("""          h('button', { type: 'button', className: 'dsq-action', disabled: busy, onClick: close }, t('back')),""",
    """          h(
            'button',
            {
              type: 'button',
              className: 'dsq-action',
              disabled: busy,
              title: t('saveAsNew'),
              onClick: () => {
                if (text.trim() === '') {
                  setError(t('textRequired'))
                  return
                }
                saveAsNew({ label: label.trim() === '' ? toLabel('', text) : label.trim(), text })
              },
            },
            t('saveAsNew'),
          ),
          h('button', { type: 'button', className: 'dsq-action', disabled: busy, onClick: close }, t('back')),""",
    "saveAsNew-btn")

# ---------------------------------------------------------------- 7. 字典
sub("""        moveHint: '拖到别的格子或页签上可换位置（仅编辑态）',
      },""",
    """        moveHint: '拖到别的格子或页签上可换位置（仅编辑态）',
        movedCell: '已移动',
      },""",
    "dict-zh")

sub("""        moveHint: 'Drag onto another card or a tab to move it (edit mode)',
      },""",
    """        moveHint: 'Drag onto another card or a tab to move it (edit mode)',
        movedCell: 'Moved',
      },""",
    "dict-en")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("ok, size =", len(src))
