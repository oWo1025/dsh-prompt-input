# -*- coding: utf-8 -*-
"""把 dsh-quick-input 的客户端半区改成 P0：气泡 + 搜索 + 键盘 + shell.overlay 槽位。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEV = r"E:\dsh\quick-input-dev"
CLIENT = os.path.join(DEV, "client.js")

src = open(CLIENT, encoding="utf-8").read()
assert len(src) > 40000, len(src)


def sub(old, new, count=1, label=""):
    global src
    got = src.count(old)
    assert got == count, f"[{label}] expected {count} got {got}: {old[:70]!r}"
    src = src.replace(old, new)


def splice(start_marker, end_marker, new_block, label=""):
    global src
    assert src.count(start_marker) == 1, f"[{label}] start marker not unique"
    assert src.count(end_marker) == 1, f"[{label}] end marker not unique"
    a = src.index(start_marker)
    b = src.index(end_marker)
    assert a < b, f"[{label}] markers out of order"
    src = src[:a] + new_block + src[b:]


# ---------------------------------------------------------------- 1. 槽位
sub("const PANEL_SLOT = 'conversation.input.overlay'",
    "const PANEL_SLOT = 'shell.overlay'",
    label="slot")

# ---------------------------------------------------------------- 2. 常量
sub("""    /**
     * 面板形态：
     *   true  → 常驻贴在输入框左边，高度与输入框卡片一致（默认；窗口太窄时退回上面浮层）
     *   false → 固定成输入框上方的一块浮层（旧形态）
     * 侧挂时渲染后自测一次：探测点落在自己身上才保留，否则退回浮层。
     */
    const SIDE_BY_SIDE = true

    /** 量不到输入框卡片高度时的兜底高度（≈ 空草稿时卡片的高度）。 */
    const DEFAULT_CARD_HEIGHT = 104

    /**
     * 面板的最小高度：3 行 × 两行文字（24px）+ 行距 + 控制栏 + 内边距。
     * 空草稿的输入框卡片约 102px，比这个矮，所以面板会上下各外扩几像素；
     * 草稿变长、卡片超过这个高度时，两者就严格等高。
     */
    const MIN_PANEL_HEIGHT = 116

    /**
     * 面板宽度：不写死，按「输入框左边到会话列左边缘」的实测空隙自适应。
     * 空隙不够就窄一点，窄到下限还放不下才退回上方浮层。
     */
    const PANEL_MIN_WIDTH = 120
    const PANEL_MAX_WIDTH = 232
    /** 面板与输入框之间的缝。 */
    const PANEL_GAP = 8""",
    """    /**
     * 气泡是「锚在 ⊞ 旁边的浮层」，不再和输入框卡片等高：
     * 宽度固定（窄窗口钳到视口内），高度上限固定，内容多了自己滚。
     */
    const PANEL_WIDTH = 420
    const PANEL_MAX_HEIGHT = 460
    /** 气泡与锚点之间的缝、以及离视口边缘的最小留白。 */
    const PANEL_GAP = 8
    const VIEWPORT_MARGIN = 12""",
    label="constants")

# ---------------------------------------------------------------- 3. CSS：面板外壳
sub(".dsq-panel{position:absolute;z-index:40;box-sizing:border-box;max-width:calc(100vw - 24px);display:flex;flex-direction:column;gap:3px;padding:4px;border-radius:var(--dsw-radius-panel,12px);background:var(--dsw-alias-bg-overlay,var(--dsw-alias-bg-layer-1,#fff));border:1px solid var(--dsw-alias-border-l2,rgba(0,0,0,.14));box-shadow:var(--dsw-elevation-soft,0 8px 28px rgba(0,0,0,.18));color:var(--dsw-alias-label-primary,#1f2328);text-align:left;font-size:11px;line-height:12px}",
    ".dsq-pop{position:fixed;z-index:60;box-sizing:border-box;display:flex;flex-direction:column;gap:6px;padding:8px;border-radius:var(--dsw-radius-panel,12px);background:var(--dsw-alias-bg-overlay,var(--dsw-alias-bg-layer-1,#fff));border:1px solid var(--dsw-alias-border-l2,rgba(0,0,0,.14));box-shadow:var(--dsw-elevation-soft,0 12px 32px rgba(0,0,0,.22));color:var(--dsw-alias-label-primary,#1f2328);text-align:left;font-size:12px;line-height:16px;pointer-events:auto;overflow:hidden}",
    label="css-panel")

# ---------------------------------------------------------------- 4. CSS：新增气泡内部样式
sub(""".dsq-muted{color:var(--dsw-alias-label-secondary,#667085)}
`""",
    """.dsq-muted{color:var(--dsw-alias-label-secondary,#667085)}
.dsq-head{display:flex;align-items:center;gap:6px;flex:none}
.dsq-search{flex:1;min-width:0;box-sizing:border-box;height:28px;padding:0 8px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.12));border-radius:8px;background:transparent;color:inherit;font-family:inherit;font-size:12px;outline:none}
.dsq-search:focus{border-color:var(--dsw-alias-brand-primary,#4d6bfe)}
.dsq-x{box-sizing:border-box;flex:none;width:24px;height:24px;padding:0;border:0;border-radius:6px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-size:14px;line-height:1;cursor:pointer}
.dsq-x:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-tabs{display:flex;flex-wrap:wrap;gap:4px;flex:none}
.dsq-tab{box-sizing:border-box;height:22px;padding:0 8px;border:1px solid transparent;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-size:11px;line-height:20px;cursor:pointer;white-space:nowrap}
.dsq-tab:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12))}
.dsq-tab-on{border-color:var(--dsw-alias-border-l2,rgba(0,0,0,.16));background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;overflow-y:auto;min-height:0;padding-right:2px}
.dsq-card{box-sizing:border-box;min-height:52px;display:flex;flex-direction:column;gap:2px;align-items:flex-start;padding:7px 8px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.1));border-radius:9px;background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:16px;text-align:left;cursor:pointer;overflow:hidden}
.dsq-card:hover,.dsq-card:focus-visible{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));border-color:var(--dsw-alias-border-l2,rgba(0,0,0,.2));outline:none}
.dsq-card-label{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;width:100%;overflow-wrap:anywhere}
.dsq-card-sub{width:100%;font-size:10px;line-height:12px;color:var(--dsw-alias-label-secondary,#667085);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dsq-card-empty{align-items:center;justify-content:center;border-style:dashed;color:var(--dsw-alias-state-idle-primary,#98a2b3);font-size:14px}
.dsq-results{display:flex;flex-direction:column;gap:2px;overflow-y:auto;min-height:0}
.dsq-item{box-sizing:border-box;display:flex;align-items:center;gap:8px;padding:6px 8px;border:1px solid transparent;border-radius:8px;background:transparent;color:inherit;font-family:inherit;font-size:12px;text-align:left;cursor:pointer}
.dsq-item:hover,.dsq-item-on{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));border-color:var(--dsw-alias-border-l1,rgba(0,0,0,.1))}
.dsq-item-label{flex:none;max-width:46%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}
.dsq-item-snippet{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--dsw-alias-label-secondary,#667085);font-size:11px}
.dsq-item-page{flex:none;font-size:10px;color:var(--dsw-alias-label-secondary,#667085);padding:1px 6px;border-radius:999px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.1))}
.dsq-foot{display:flex;align-items:center;gap:6px;flex:none;font-size:10px;line-height:14px;color:var(--dsw-alias-label-secondary,#667085)}
.dsq-foot-grow{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
`""",
    label="css-inner")

# ---------------------------------------------------------------- 5. 字典补词
sub("""        insertConflict: '草稿刚变过，再点一次',
      },""",
    """        insertConflict: '草稿刚变过，再点一次',
        searchPlaceholder: '搜索 Prompt…',
        noResults: '没有匹配「{q}」',
        searchCount: '{n} 条结果 · ↑↓ 选择 · Enter 插入',
        editCellShort: '✎ 点击可编辑',
      },""",
    label="dict-zh")

sub("""        insertConflict: 'The draft just changed — click again',
      },""",
    """        insertConflict: 'The draft just changed — click again',
        searchPlaceholder: 'Search prompts…',
        noResults: 'Nothing matches "{q}"',
        searchCount: '{n} results · ↑↓ to move · Enter to insert',
        editCellShort: '✎ click to edit',
      },""",
    label="dict-en")

# ---------------------------------------------------------------- 6. 桥 + 搜索态 + 摊平/搜索/定位
sub("""    const flashTimers = new Map()""",
    """    const flashTimers = new Map()

    // ------------------------------------------------------------ 跨槽位桥

    /**
     * ⊞ 挂在 `conversation.input.left`（会话作用域），拿得到 sessionId / inputActions；
     * 气泡挂在 `shell.overlay`（root 作用域），这些 props 都拿不到。
     * 两个半区同属一个包、同一个客户端模块，所以用这份模块级桥接传递。
     */
    const bridge = {
      sessionId: null,
      inputActions: null,
      phase: undefined,
      /** ⊞ 按钮节点：气泡靠它定位。 */
      node: null,
    }

    /** 每个会话各自的搜索态：`{ query, active }`。切会话不串台。 */
    const searchState = new Map()

    function readSearch(sessionId) {
      return searchState.get(sessionId) ?? { query: '', active: 0 }
    }

    function writeSearch(sessionId, patch) {
      searchState.set(sessionId, { ...readSearch(sessionId), ...patch })
    }

    /** 一页页摊平成可搜索的条目。 */
    function flattenPages(pages) {
      const items = []
      pages.forEach((page, pageIndex) => {
        page.cells.forEach((cell, cellIndex) => {
          if (!cell) return
          items.push({ pageIndex, cellIndex, page: page.title, label: cell.label, text: cell.text })
        })
      })
      return items
    }

    /** 搜索：label 命中排在正文命中前面，同档按页序、格序。 */
    function searchPages(pages, query) {
      const q = String(query || '').trim().toLowerCase()
      if (q === '') return null
      const hits = []
      for (const item of flattenPages(pages)) {
        const inLabel = item.label.toLowerCase().indexOf(q) !== -1
        const inText = item.text.toLowerCase().indexOf(q) !== -1
        if (!inLabel && !inText) continue
        hits.push({ item, rank: inLabel ? 0 : 1 })
      }
      hits.sort(
        (a, b) =>
          a.rank - b.rank ||
          a.item.pageIndex - b.item.pageIndex ||
          a.item.cellIndex - b.item.cellIndex,
      )
      return hits.map((hit) => hit.item)
    }

    /** 一行摘要：压平空白后截断。 */
    function snippet(text) {
      const flat = String(text || '').replace(/\\s+/g, ' ').trim()
      return flat.length > 64 ? `${flat.slice(0, 63)}…` : flat
    }

    /** 收起面板（两个半区共用）。 */
    function closePanel(sessionId) {
      store.open.set(sessionId, false)
      store.editing.set(sessionId, null)
      store.editMode.set(sessionId, false)
      store.flash.delete(sessionId)
      writeOpenFlag(false)
      store.emit()
    }""",
    label="bridge")

# ---------------------------------------------------------------- 7. 位置自测 → 气泡定位
splice(
    "    // ------------------------------------------------------------ 位置自测",
    "    // ------------------------------------------------------------ hook 小工具",
    """    // ------------------------------------------------------------ 气泡定位

    /**
     * 气泡位置：默认贴在 ⊞ 右边；右边放不下翻到左边；上下取空间大的一侧。
     * 用 fixed 定位——气泡在 shell.overlay 这一层，不受 composer 卡片裁剪。
     */
    function popoverStyle(anchor) {
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
      return style
    }

""",
    label="position",
)

# ---------------------------------------------------------------- 8. ⊞：把会话能力递出去
splice(
    "    function QuickToggle(props) {",
    "    // ------------------------------------------------------------ 单格编辑器",
    """    function QuickToggle(props) {
      useStore()
      const t = translator(props)
      const sessionId = props.sessionId
      const open = isOpen(sessionId)
      const btnRef = React.useRef(null)
      // 只在槽位真的给了 useInput 时才订阅输入状态；拿不到当未知。
      const phase = typeof props.useInput === 'function' ? props.useInput(selectPhase) : undefined

      // 每次渲染都把最新的会话能力递给浮层（气泡在另一个作用域里）。
      React.useEffect(() => {
        bridge.sessionId = sessionId ?? null
        bridge.inputActions = props.inputActions ?? null
        bridge.phase = phase
        bridge.node = btnRef.current ?? bridge.node
      })

      return h(
        React.Fragment,
        null,
        h('style', null, CSS),
        h(
          'button',
          {
            ref: btnRef,
            type: 'button',
            className: open ? 'dsq-btn dsq-btn-on' : 'dsq-btn',
            style: { WebkitAppearance: 'none' },
            title: open ? t('toggleHide') : t('toggleShow'),
            'aria-label': t('toggleAria'),
            'aria-expanded': open ? 'true' : 'false',
            onMouseDown: keepFocus,
            onClick: () => {
              const next = open !== true
              // 先递能力再开面板：浮层的第一次渲染就能拿到 sessionId。
              bridge.sessionId = sessionId ?? null
              bridge.inputActions = props.inputActions ?? null
              bridge.phase = phase
              bridge.node = btnRef.current ?? bridge.node
              store.open.set(sessionId, next)
              writeOpenFlag(next)
              if (next) ensureDoc(false)
              store.emit()
            },
          },
          h(GridIcon, null),
        ),
      )
    }

""",
    label="toggle",
)

print("part 1 done, size =", len(src))
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
