# -*- coding: utf-8 -*-
"""0.2.3-a：加显式拖拽把手（六点 grip），标题行不再充当把手。"""
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


# 1) 样式：加 grip、加拖拽态；标题行不再是把手
sub("""/* 拖拽：只有标题栏是把手，输入框和按钮不拖 */
.dsq-head{cursor:grab;user-select:none}
.dsq-head:active{cursor:grabbing}
.dsq-head input,.dsq-head button{cursor:auto}""",
    """/* 拖拽：标题行被搜索框占满，所以左上角单独给一个六点把手 */
.dsq-grip{flex:none;width:16px;height:30px;display:grid;place-items:center;color:var(--dsw-alias-label-caption,#98a2b3);cursor:grab;border-radius:var(--dsw-radius-sm,8px);user-select:none;transition:background-color .12s ease,color .12s ease}
.dsq-grip:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));color:var(--dsw-alias-label-secondary,#667085)}
.dsq-grip:active{cursor:grabbing}
.dsq-card-drag{opacity:.45}
.dsq-card-over{border-color:var(--dsw-alias-brand-primary,#4d6bfe);border-style:dashed}
.dsq-tab-over{background:color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 18%,transparent);color:var(--dsw-alias-label-primary,#1f2328)}""",
    "css")

# 2) 字典
sub("""        shortcutToggle: '打开 / 收起快捷输入',
      },""",
    """        shortcutToggle: '打开 / 收起快捷输入',
        dragHint: '拖动这里移动面板（双击复位）',
        saveAsNew: '另存为新格',
        pageFull: '这一页满了（9 格），先腾一个格子',
        moveHint: '拖到别的格子或页签上可换位置（仅编辑态）',
      },""",
    "dict-zh")

sub("""        shortcutToggle: 'Toggle quick input',
      },""",
    """        shortcutToggle: 'Toggle quick input',
        dragHint: 'Drag here to move the panel (double-click to reset)',
        saveAsNew: 'Save as new cell',
        pageFull: 'This page is full (9 cells)',
        moveHint: 'Drag onto another card or a tab to move it (edit mode)',
      },""",
    "dict-en")

# 3) 头部：把拖拽事件从整行挪到 grip 上
sub("""        { className: 'dsq-head', onPointerDown: onHeadPointerDown, onDoubleClick: resetPosition },
        h(
          'div',
          { className: 'dsq-searchwrap' },""",
    """        { className: 'dsq-head' },
        h(
          'div',
          {
            className: 'dsq-grip',
            title: t('dragHint'),
            'aria-hidden': 'true',
            onPointerDown: onHeadPointerDown,
            onDoubleClick: resetPosition,
          },
          h(
            'svg',
            { width: 10, height: 14, viewBox: '0 0 10 14', fill: 'currentColor', 'aria-hidden': 'true' },
            [0, 1, 2].map((row) =>
              [0, 1].map((column) =>
                h('circle', { key: `${row}-${column}`, cx: 2 + column * 5, cy: 2 + row * 5, r: 1.5 }),
              ),
            ),
          ),
        ),
        h(
          'div',
          { className: 'dsq-searchwrap' },""",
    "head-grip")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("ok, size =", len(src))
