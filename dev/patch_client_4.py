# -*- coding: utf-8 -*-
"""P0.1：页签移到底部、内容区定高、改用原生浅白表面、胶囊页签、整体视觉打磨。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = r"E:\dsh\quick-input-dev\client.js"
src = open(CLIENT, encoding="utf-8").read()


def sub(old, new, label=""):
    global src
    assert src.count(old) == 1, f"[{label}] expected 1 got {src.count(old)}"
    src = src.replace(old, new)


def splice(start_marker, end_marker, block, label=""):
    global src
    assert src.count(start_marker) == 1, f"[{label}] start not unique"
    assert src.count(end_marker) == 1, f"[{label}] end not unique"
    a, b = src.index(start_marker), src.index(end_marker)
    assert a < b, f"[{label}] order"
    src = src[:a] + block + src[b:]


# ---------------------------------------------------------------- 1. 整块样式重写
CSS = '''    const CSS = `
.dsq-btn{box-sizing:border-box;width:28px;height:28px;flex:none;display:grid;place-items:center;padding:0;border:0;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);cursor:pointer;transition:background-color .12s ease,color .12s ease}
.dsq-btn:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-btn-on{color:var(--dsw-alias-brand-primary,#4d6bfe);background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.1))}

.dsq-pop{position:fixed;z-index:60;box-sizing:border-box;display:flex;flex-direction:column;gap:10px;padding:10px;border-radius:var(--dsw-radius-lg,16px);background:var(--dsw-alias-bg-layer-2,#fff);color:var(--dsw-alias-label-primary,#1f2328);text-align:left;font-size:12px;line-height:16px;pointer-events:auto;overflow:hidden;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));box-shadow:var(--dsw-elevation-panel,0 12px 32px rgba(16,24,40,.14));animation:dsq-in .14s ease-out}
@keyframes dsq-in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.dsq-pop{animation:none}}

.dsq-head{display:flex;align-items:center;gap:6px;flex:none}
.dsq-searchwrap{position:relative;flex:1;min-width:0;display:flex}
.dsq-searchicon{position:absolute;left:9px;top:50%;transform:translateY(-50%);color:var(--dsw-alias-label-caption,#98a2b3);pointer-events:none}
.dsq-search{box-sizing:border-box;width:100%;height:30px;padding:0 10px 0 28px;border:1px solid transparent;border-radius:var(--dsw-radius-md,10px);background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.07));color:inherit;font-family:inherit;font-size:12px;line-height:16px;outline:none;transition:border-color .12s ease,background-color .12s ease}
.dsq-search::placeholder{color:var(--dsw-alias-label-caption,#98a2b3)}
.dsq-search:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));background:var(--dsw-alias-bg-layer-2,#fff)}
.dsq-x{box-sizing:border-box;flex:none;width:26px;height:26px;padding:0;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-size:15px;line-height:1;cursor:pointer}
.dsq-x:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}

/* 内容区：普通态定高 3 行（换页高度不变），编辑态才自适应并可滚 */
.dsq-body{flex:0 0 auto;min-height:0;display:flex;flex-direction:column;overflow:hidden}
.dsq-body-auto{flex:1 1 auto;min-height:120px;overflow-y:auto;scrollbar-width:thin}
.dsq-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:54px;gap:6px;height:174px;overflow-y:auto;padding-right:2px;scrollbar-width:thin}
.dsq-card{box-sizing:border-box;display:flex;flex-direction:column;gap:1px;align-items:flex-start;justify-content:center;padding:6px 8px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));border-radius:var(--dsw-radius-md,10px);background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:16px;text-align:left;cursor:pointer;overflow:hidden;transition:background-color .12s ease,border-color .12s ease,transform .1s ease}
.dsq-card:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));border-color:var(--dsw-alias-border-l2,rgba(0,0,0,.16))}
.dsq-card:active{transform:scale(.985)}
.dsq-card:focus-visible{outline:none;border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));box-shadow:0 0 0 2px color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 22%,transparent)}
.dsq-card-label{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;width:100%;overflow-wrap:anywhere;font-weight:500}
.dsq-card-sub{width:100%;font-size:10px;line-height:12px;color:var(--dsw-alias-label-caption,#98a2b3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dsq-card-empty{align-items:center;justify-content:center;border-style:dashed;color:var(--dsw-alias-label-caption,#98a2b3);font-size:14px;font-weight:400}

.dsq-results{display:flex;flex-direction:column;gap:2px;height:174px;overflow-y:auto;padding-right:2px;scrollbar-width:thin}
.dsq-item{box-sizing:border-box;display:flex;align-items:center;gap:8px;height:34px;flex:none;padding:0 8px;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:inherit;font-family:inherit;font-size:12px;text-align:left;cursor:pointer}
.dsq-item:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1))}
.dsq-item-on{background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.1))}
.dsq-item-label{flex:none;max-width:46%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}
.dsq-item-snippet{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--dsw-alias-label-secondary,#667085);font-size:11px}
.dsq-item-page{flex:none;font-size:10px;line-height:16px;color:var(--dsw-alias-label-caption,#98a2b3);padding:0 6px;border-radius:999px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08))}

/* 页签行（在底部）：位置固定，换页不会上下跳 */
.dsq-tabsrow{display:flex;align-items:center;gap:6px;flex:none;min-width:0}
.dsq-tabs{display:flex;align-items:center;gap:4px;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none;padding:1px}
.dsq-tabs::-webkit-scrollbar{display:none}
.dsq-tab{box-sizing:border-box;flex:none;height:24px;padding:0 9px;border:1px solid transparent;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-family:inherit;font-size:11.5px;line-height:22px;cursor:pointer;white-space:nowrap;transition:background-color .12s ease,color .12s ease,border-color .12s ease}
.dsq-tab:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-tab-on{background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.12));border-color:var(--dsw-alias-border-l2,rgba(0,0,0,.12));color:var(--dsw-alias-label-primary,#1f2328);font-weight:600}
.dsq-tab:focus-visible{outline:none;border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe))}
.dsq-count{flex:none;max-width:132px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px;line-height:16px;color:var(--dsw-alias-label-caption,#98a2b3);font-variant-numeric:tabular-nums}
.dsq-mini{box-sizing:border-box;flex:none;height:24px;min-width:24px;padding:0 7px;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-family:inherit;font-size:12px;line-height:1;cursor:pointer}
.dsq-mini:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-mini:disabled{opacity:.45;cursor:default}

/* 编辑态 */
.dsq-row{display:flex;align-items:center;gap:6px}
.dsq-row-label{flex:none;font-size:11px;color:var(--dsw-alias-label-secondary,#667085)}
.dsq-input,.dsq-textarea{box-sizing:border-box;width:100%;padding:6px 9px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.1));border-radius:var(--dsw-radius-sm,8px);background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.06));color:inherit;font-family:inherit;font-size:12px;line-height:18px;outline:none;transition:border-color .12s ease,background-color .12s ease}
.dsq-textarea{resize:vertical;min-height:96px;white-space:pre-wrap}
.dsq-input:focus,.dsq-textarea:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary,#4d6bfe));background:var(--dsw-alias-bg-layer-2,#fff)}
.dsq-actions{display:flex;align-items:center;gap:6px}
.dsq-action{box-sizing:border-box;height:28px;padding:0 12px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.1));border-radius:var(--dsw-radius-sm,8px);background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:18px;cursor:pointer}
.dsq-action:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1))}
.dsq-action-primary{border-color:transparent;background:var(--dsw-alias-brand-primary,#4d6bfe);color:#fff}
.dsq-action-primary:hover{background:var(--dsw-alias-brand-primary,#4d6bfe);opacity:.92}
.dsq-ok{color:var(--dsw-alias-state-success-primary,#12b76a)}
.dsq-err{color:var(--dsw-alias-state-error-primary,#d92d20)}
.dsq-muted{color:var(--dsw-alias-label-secondary,#667085)}
`

'''

splice("    const CSS = `", "    // ------------------------------------------------------------ 小工具", CSS, "css")

# ---------------------------------------------------------------- 2. 面板：头部/内容/页签行 的结构与顺序
HEAD_OLD = """      const head = h(
        'div',
        { className: 'dsq-head' },
        h('input', {"""
HEAD_NEW = """      const head = h(
        'div',
        { className: 'dsq-head' },
        h(
          'div',
          { className: 'dsq-searchwrap' },
          h(
            'svg',
            {
              className: 'dsq-searchicon',
              width: 14,
              height: 14,
              viewBox: '0 0 24 24',
              fill: 'none',
              stroke: 'currentColor',
              strokeWidth: 2.2,
              'aria-hidden': 'true',
            },
            h('circle', { cx: 11, cy: 11, r: 7 }),
            h('path', { d: 'M20 20l-3.5-3.5' }),
          ),
          h('input', {"""
sub(HEAD_OLD, HEAD_NEW, "head-open")

# 搜索框闭合：把 input 收进 wrap
sub("""            }
          },
        }),
        h(
          'button',
          {
            type: 'button',
            className: 'dsq-x',""",
    """            }
          },
        }),
        ),
        h(
          'button',
          {
            type: 'button',
            className: 'dsq-x',""",
    "head-close")

# 换掉旧的底栏（foot），改成底部的页签行
OLD_FOOT_START = "      const foot = h("
OLD_FOOT_END = "      return h(\n        React.Fragment,"
a = src.index(OLD_FOOT_START)
b = src.index(OLD_FOOT_END, a)
assert a < b

TABSROW = """      // 页签放在最后一行：气泡底部锚定，换页时这一行不会上下移动。
      const tabsRow = h(
        'div',
        { className: 'dsq-tabsrow' },
        tabs,
        h(
          'span',
          {
            className: 'dsq-count',
            title: flash
              ? flash.text
              : t('pageHint', {
                  title: page ? page.title : '',
                  index: pageIndex + 1,
                  total: Math.max(pages.length, 1),
                }),
          },
          flash
            ? h('span', { className: flash.kind === 'ok' ? 'dsq-ok' : 'dsq-err' }, flash.text)
            : `${pageIndex + 1}/${Math.max(pages.length, 1)}`,
        ),
        editMode && pages.length < MAX_PAGES
          ? h(
              'button',
              {
                type: 'button',
                className: 'dsq-mini',
                title: t('addPage'),
                onMouseDown: keepFocus,
                onClick: addPage,
              },
              '＋',
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

"""
src = src[:a] + TABSROW + src[b:]

# 渲染体：head → body → tabsRow；body 高度由 CSS 定住，编辑态才自适应
OLD_RETURN = """          head,
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
        ),"""
NEW_RETURN = """          head,
          h('div', { className: editing !== null ? 'dsq-body dsq-body-auto' : 'dsq-body' }, body),
          tabsRow,
        ),"""
sub(OLD_RETURN, NEW_RETURN, "return-body")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("patched, size =", len(src))
