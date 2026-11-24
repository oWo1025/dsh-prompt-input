# -*- coding: utf-8 -*-
"""P1：悬停预览 + 拖拽位置记忆 + 全局快捷键。"""
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
    assert got == 1, f"[{label}] expected 1 got {got}: {old[:60]!r}"
    src = src.replace(old, new)


def splice(start, end, block, label=""):
    global src
    assert src.count(start) == 1, f"[{label}] start"
    assert src.count(end) == 1, f"[{label}] end"
    a, b = src.index(start), src.index(end)
    assert a < b, f"[{label}] order"
    src = src[:a] + block + src[b:]


# ---------------------------------------------------------------- 1. 样式
sub(""".dsq-muted{color:var(--dsw-alias-label-secondary,#667085)}
`""",
    """.dsq-muted{color:var(--dsw-alias-label-secondary,#667085)}

/* 拖拽：只有标题栏是把手，输入框和按钮不拖 */
.dsq-head{cursor:grab;user-select:none}
.dsq-head:active{cursor:grabbing}
.dsq-head input,.dsq-head button{cursor:auto}

/* 悬停预览：固定位置 + 不接收指针，鼠标可以径直移向下一张卡 */
.dsq-preview{position:fixed;z-index:61;box-sizing:border-box;padding:10px 12px;border-radius:var(--dsw-radius-md,12px);background:var(--dsw-alias-bg-layer-2,#fff);border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));box-shadow:var(--dsw-elevation-panel,0 12px 32px rgba(16,24,40,.14));color:var(--dsw-alias-label-primary,#1f2328);font-size:12px;line-height:18px;pointer-events:none;overflow:hidden;animation:dsq-fade .12s ease-out}
@keyframes dsq-fade{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.dsq-preview{animation:none}}
.dsq-preview-title{font-weight:600;margin-bottom:2px}
.dsq-preview-meta{font-size:10px;line-height:14px;color:var(--dsw-alias-label-caption,#98a2b3);margin-bottom:6px}
.dsq-preview-text{white-space:pre-wrap;overflow-wrap:anywhere;color:var(--dsw-alias-label-secondary,#667085);max-height:168px;overflow:hidden;-webkit-mask-image:linear-gradient(#000 74%,transparent);mask-image:linear-gradient(#000 74%,transparent)}
.dsq-preview-foot{margin-top:7px;font-size:10px;line-height:14px;color:var(--dsw-alias-label-caption,#98a2b3)}
`""",
    "css")

# ---------------------------------------------------------------- 2. 位置记忆 + 气泡定位
splice(
    "    // ------------------------------------------------------------ 气泡定位",
    "    // ------------------------------------------------------------ hook 小工具",
    """    // ------------------------------------------------------------ 位置记忆

    /** 拖拽位移（相对锚点）按窗口宽度分档存，换分辨率不会飘到屏幕外。 */
    const POS_KEY = 'quick-input.pos.v1'

    function widthBucket() {
      const width = window.innerWidth || 1280
      return width < 900 ? 's' : width < 1400 ? 'm' : 'l'
    }

    function loadPos() {
      try {
        const raw = window.localStorage ? window.localStorage.getItem(POS_KEY) : null
        if (!raw) return null
        const all = JSON.parse(raw) || {}
        const value = all[widthBucket()]
        if (!value || typeof value.dx !== 'number' || typeof value.dy !== 'number') return null
        return { dx: value.dx, dy: value.dy }
      } catch {
        return null
      }
    }

    function savePos(value) {
      try {
        if (!window.localStorage) return
        const raw = window.localStorage.getItem(POS_KEY)
        const all = raw ? JSON.parse(raw) || {} : {}
        if (value === null) delete all[widthBucket()]
        else all[widthBucket()] = { dx: Math.round(value.dx), dy: Math.round(value.dy) }
        window.localStorage.setItem(POS_KEY, JSON.stringify(all))
      } catch {
        /* 存不了就算了 */
      }
    }

    // ------------------------------------------------------------ 气泡定位

    /**
     * 气泡位置：默认贴在 ⊞ 右边；右边放不下翻到左边；上下取空间大的一侧。
     * 用 fixed 定位——气泡在 shell.overlay 这一层，不受 composer 卡片裁剪。
     * 拖动过就叠加位移（dy 为正＝向下），并钳在视口内。
     */
    function popoverStyle(anchor, drag) {
      const vw = window.innerWidth || 1280
      const vh = window.innerHeight || 800
      const width = Math.max(300, Math.min(PANEL_WIDTH, vw - VIEWPORT_MARGIN * 2))
      let left = anchor.right + PANEL_GAP
      if (left + width > vw - VIEWPORT_MARGIN) left = anchor.left - PANEL_GAP - width
      left = Math.max(VIEWPORT_MARGIN, Math.min(left, vw - width - VIEWPORT_MARGIN))
      const above = anchor.top - VIEWPORT_MARGIN
      const below = vh - anchor.bottom - VIEWPORT_MARGIN
      const putAbove = above >= 240 || above >= below
      const space = Math.max(200, putAbove ? above : below)
      const style = { left: left, width: width, maxHeight: Math.min(PANEL_MAX_HEIGHT, space) }
      if (putAbove) style.bottom = Math.max(VIEWPORT_MARGIN, vh - anchor.top)
      else style.top = Math.max(VIEWPORT_MARGIN, anchor.bottom)

      if (drag) {
        const dx = Number(drag.dx) || 0
        const dy = Number(drag.dy) || 0
        style.left = Math.max(
          VIEWPORT_MARGIN - 40,
          Math.min(Number(style.left) + dx, vw - width - VIEWPORT_MARGIN + 40),
        )
        if (putAbove) {
          // bottom 越大越靠上，所以向下拖是减。
          style.bottom = Math.max(160, Math.min(Number(style.bottom) - dy, vh - VIEWPORT_MARGIN))
        } else {
          style.top = Math.max(VIEWPORT_MARGIN, Math.min(Number(style.top) + dy, vh - 160))
        }
      }
      return style
    }

""",
    "position",
)

# ---------------------------------------------------------------- 3. 面板状态
sub("""      const [anchor, setAnchor] = React.useState(null)
      const rootRef = React.useRef(null)""",
    """      const [anchor, setAnchor] = React.useState(null)
      const [drag, setDrag] = React.useState(() => loadPos())
      const [preview, setPreview] = React.useState(null)
      const timers = React.useRef({ show: 0, hide: 0, last: 0 })
      const rootRef = React.useRef(null)

      // 关掉面板就把预览和计时器一起清掉。
      React.useEffect(() => {
        if (open) return
        setPreview(null)
        const current = timers.current
        if (current.show) clearTimeout(current.show)
        if (current.hide) clearTimeout(current.hide)
        current.show = 0
        current.hide = 0
      }, [open])""",
    "panel-state")

# ---------------------------------------------------------------- 4. 悬停预览 / 拖拽逻辑
sub("""      const insert = (cell) => {
        const result = insertIntoDraft(bridge.inputActions, cell.text, bridge.phase)
        if (result.ok === true) setFlash(sessionId, 'ok', t('inserted', { text: toLabel('', cell.text) }))
        else setFlash(sessionId, 'err', result.reason)
      }""",
    """      const insert = (cell) => {
        stopPreview()
        const result = insertIntoDraft(bridge.inputActions, cell.text, bridge.phase)
        if (result.ok === true) setFlash(sessionId, 'ok', t('inserted', { text: toLabel('', cell.text) }))
        else setFlash(sessionId, 'err', result.reason)
      }

      // —— 悬停预览 ——
      // 450ms 首次、120ms 相邻切换、180ms 离开宽限；预览不接收指针，所以绝不挡鼠标。
      const hoverCapable = (() => {
        try {
          return typeof window.matchMedia === 'function' ? window.matchMedia('(hover: hover)').matches : true
        } catch {
          return true
        }
      })()

      const stopPreview = () => {
        const current = timers.current
        if (current.show) {
          clearTimeout(current.show)
          current.show = 0
        }
        if (current.hide) {
          clearTimeout(current.hide)
          current.hide = 0
        }
      }

      const hoverEnter = (event, cell) => {
        if (!hoverCapable) return
        const node = event && event.currentTarget ? event.currentTarget : null
        if (!node || typeof node.getBoundingClientRect !== 'function') return
        const rect = node.getBoundingClientRect()
        const root = rootRef.current
        const rootRect = root && root.getBoundingClientRect ? root.getBoundingClientRect() : rect
        const current = timers.current
        if (current.hide) {
          clearTimeout(current.hide)
          current.hide = 0
        }
        if (current.show) clearTimeout(current.show)
        const delay = Date.now() - (current.last || 0) < 600 ? 120 : 450
        current.show = setTimeout(() => {
          current.show = 0
          current.last = Date.now()
          setPreview({
            label: cell.label,
            text: cell.text,
            page: cell.page,
            top: rect.top,
            left: rootRect.left,
            right: rootRect.right,
          })
        }, delay)
      }

      const hoverLeave = () => {
        const current = timers.current
        if (current.show) {
          clearTimeout(current.show)
          current.show = 0
        }
        if (current.hide) clearTimeout(current.hide)
        current.hide = setTimeout(() => {
          current.hide = 0
          setPreview(null)
        }, 180)
      }

      // —— 拖拽（只有标题栏是把手） ——
      const onHeadPointerDown = (event) => {
        if (!event || event.button !== 0) return
        const target = event.target
        if (target && typeof target.closest === 'function' && target.closest('input,button,textarea')) return
        const startX = event.clientX
        const startY = event.clientY
        const base = drag || { dx: 0, dy: 0 }
        let latest = base
        let moved = false
        const onMove = (moveEvent) => {
          const dx = moveEvent.clientX - startX
          const dy = moveEvent.clientY - startY
          if (!moved && Math.abs(dx) + Math.abs(dy) < 4) return
          moved = true
          latest = { dx: base.dx + dx, dy: base.dy + dy }
          setDrag(latest)
        }
        const onUp = () => {
          document.removeEventListener('pointermove', onMove)
          document.removeEventListener('pointerup', onUp)
          if (moved) savePos(latest)
        }
        try {
          if (event.currentTarget && typeof event.currentTarget.setPointerCapture === 'function') {
            event.currentTarget.setPointerCapture(event.pointerId)
          }
        } catch {
          /* 捕获失败也能拖 */
        }
        document.addEventListener('pointermove', onMove)
        document.addEventListener('pointerup', onUp)
      }

      const resetPosition = () => {
        savePos(null)
        setDrag(null)
        setPreview(null)
      }""",
    "hover-drag")

# ---------------------------------------------------------------- 5. 挂到渲染上
sub("""        { className: 'dsq-head' },""",
    """        { className: 'dsq-head', onPointerDown: onHeadPointerDown, onDoubleClick: resetPosition },""",
    "head-props")

sub("""          onChange: (event) => {
            writeSearch(sessionId, { query: event.target.value, active: 0 })
            store.emit()
          },""",
    """          onChange: (event) => {
            setPreview(null)
            writeSearch(sessionId, { query: event.target.value, active: 0 })
            store.emit()
          },""",
    "search-change")

sub("""                    title: cell.text,
                    onMouseDown: keepFocus,
                    onClick: () => (editMode ? openEditor(index) : insert(cell)),""",
    """                    title: cell.text,
                    onMouseDown: keepFocus,
                    onMouseEnter: (event) =>
                      hoverEnter(event, {
                        label: cell.label,
                        text: cell.text,
                        page: page ? page.title : '',
                      }),
                    onMouseLeave: hoverLeave,
                    onClick: () => (editMode ? openEditor(index) : insert(cell)),""",
    "card-hover")

sub("""            style: popoverStyle(anchor),""",
    """            style: popoverStyle(anchor, drag),""",
    "style-call")

sub("""          head,
          h('div', { className: editing !== null ? 'dsq-body dsq-body-auto' : 'dsq-body' }, body),
          tabsRow,
        ),
      )""",
    """          head,
          h('div', { className: editing !== null ? 'dsq-body dsq-body-auto' : 'dsq-body' }, body),
          tabsRow,
        ),
        previewNode,
      )""",
    "render")

# 预览节点：贴在气泡外侧，不接收指针
sub("""      return h(
        React.Fragment,
        null,
        h('style', null, CSS),
        h(
          'div',
          {
            ref: rootRef,
            className: 'dsq-pop',""",
    """      let previewNode = null
      if (preview !== null) {
        const vw = window.innerWidth || 1280
        const vh = window.innerHeight || 800
        const width = 300
        const gap = 10
        let left = preview.right + gap
        if (left + width > vw - VIEWPORT_MARGIN) left = preview.left - gap - width
        left = Math.max(VIEWPORT_MARGIN, Math.min(left, vw - width - VIEWPORT_MARGIN))
        const top = Math.max(VIEWPORT_MARGIN, Math.min(preview.top, vh - 240))
        const raw = String(preview.text || '')
        previewNode = h(
          'div',
          { className: 'dsq-preview', style: { left: left, top: top, width: width }, 'aria-hidden': 'true' },
          h('div', { className: 'dsq-preview-title' }, preview.label),
          h('div', { className: 'dsq-preview-meta' }, t('previewMeta', { page: preview.page, n: raw.length })),
          h('div', { className: 'dsq-preview-text' }, raw.length > 360 ? `${raw.slice(0, 360)}…` : raw),
          h('div', { className: 'dsq-preview-foot' }, t('previewHint')),
        )
      }

      return h(
        React.Fragment,
        null,
        h('style', null, CSS),
        h(
          'div',
          {
            ref: rootRef,
            className: 'dsq-pop',""",
    "preview-node")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("p1 client patched, size =", len(src))
