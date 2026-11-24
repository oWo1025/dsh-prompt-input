# -*- coding: utf-8 -*-
"""0.2.6：修悬停上移被裁；入口图标换成「三张叠卡」；编辑/关闭按钮改 SVG 图标。"""
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


def splice(start, end, block, label=""):
    global src
    assert src.count(start) == 1, f"[{label}] start"
    assert src.count(end) == 1, f"[{label}] end"
    a, b = src.index(start), src.index(end)
    assert a < b, f"[{label}] order"
    src = src[:a] + block + src[b:]


# ---------------------------------------------------------------- 1. 裁剪修复
sub(""".dsq-body{flex:0 0 auto;min-height:0;display:flex;flex-direction:column;overflow:hidden}""",
    """.dsq-body{flex:0 0 auto;min-height:0;display:flex;flex-direction:column;overflow:visible}""",
    "body-overflow")

sub(""".dsq-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:52px;gap:6px;height:168px;overflow-y:auto;padding-right:2px;scrollbar-width:thin}""",
    """.dsq-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:52px;gap:6px;height:168px;overflow:visible}""",
    "grid-overflow")

# ---------------------------------------------------------------- 2. 编辑态按钮的激活底色
sub(""".dsq-mini:disabled{opacity:.45;cursor:default}""",
    """.dsq-mini:disabled{opacity:.45;cursor:default}
.dsq-mini-on{background:color-mix(in srgb,var(--dsw-alias-brand-primary,#4d6bfe) 14%,transparent);color:var(--dsw-alias-brand-primary,#4d6bfe)}""",
    "mini-on")

# ---------------------------------------------------------------- 3. 图标：三张叠卡 + 铅笔 / 对勾 / 关闭
splice(
    "    /** 3×3 圆点：一眼就是「九宫格」。 */",
    "    // ------------------------------------------------------------ ⊞ 开关",
    """    /** 入口图标：两张叠起来的卡片 + 两行字，比九点阵更像「一叠 prompt 卡」。 */
    function GridIcon() {
      return h(
        'svg',
        { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', stroke: 'currentColor', 'aria-hidden': 'true' },
        h('rect', {
          x: 4.9,
          y: 1.6,
          width: 9.5,
          height: 6.6,
          rx: 1.9,
          strokeWidth: 1.3,
          opacity: 0.45,
        }),
        h('rect', { x: 1.6, y: 6.3, width: 9.5, height: 6.6, rx: 1.9, strokeWidth: 1.3 }),
        h('path', {
          d: 'M3.9 9.1h4.4M3.9 11.2h2.8',
          strokeWidth: 1.2,
          strokeLinecap: 'round',
        }),
      )
    }

    /** 编辑：铅笔（描边风格，和其余图标统一 1.8 描边、14px 尺寸）。 */
    function PencilIcon() {
      return h(
        'svg',
        {
          width: 14,
          height: 14,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 1.8,
          strokeLinecap: 'round',
          strokeLinejoin: 'round',
          'aria-hidden': 'true',
        },
        h('path', { d: 'M4 20h4L18.5 9.5a2.8 2.8 0 0 0-4-4L4 16v4z' }),
        h('path', { d: 'M13.5 6.5l4 4' }),
      )
    }

    /** 编辑完成。 */
    function CheckIcon() {
      return h(
        'svg',
        {
          width: 14,
          height: 14,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 2,
          strokeLinecap: 'round',
          strokeLinejoin: 'round',
          'aria-hidden': 'true',
        },
        h('path', { d: 'M20 6L9 17l-5-5' }),
      )
    }

    /** 关闭。 */
    function CloseIcon() {
      return h(
        'svg',
        {
          width: 13,
          height: 13,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 1.9,
          strokeLinecap: 'round',
          'aria-hidden': 'true',
        },
        h('path', { d: 'M6 6l12 12M18 6L6 18' }),
      )
    }

""",
    "icons",
)

# ---------------------------------------------------------------- 4. 按钮用图标
sub("""            onMouseDown: keepFocus,
            onClick: () => closePanel(sessionId),
          },
          '×',
        ),""",
    """            onMouseDown: keepFocus,
            onClick: () => closePanel(sessionId),
          },
          h(CloseIcon, null),
        ),""",
    "close-btn")

sub("""            className: 'dsq-mini',
            title: editMode ? t('finishEdit') : t('editPresets'),""",
    """            className: editMode ? 'dsq-mini dsq-mini-on' : 'dsq-mini',
            title: editMode ? t('finishEdit') : t('editPresets'),""",
    "edit-btn-class")

sub("""          editMode ? t('done') : '✎',
        ),""",
    """          editMode ? h(CheckIcon, null) : h(PencilIcon, null),
        ),""",
    "edit-btn-icon")

# ---------------------------------------------------------------- 5. 版本
sub("const CLIENT_BUILD = '0.2.5+build1'", "const CLIENT_BUILD = '0.2.6+build1'", "build")
open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.5'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.5'", "const VERSION = '0.2.6'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.6"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

# ---------------------------------------------------------------- 6. 插件列表图标
ICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="快捷输入">
  <g fill="none" stroke="#4d6bfe" stroke-linejoin="round">
    <rect x="7.4" y="2.4" width="14.2" height="9.9" rx="2.9" stroke-width="1.9" opacity="0.45"/>
    <rect x="2.4" y="9.5" width="14.2" height="9.9" rx="2.9" stroke-width="1.9"/>
    <path d="M5.9 13.7h6.6M5.9 16.9h4.2" stroke-width="1.8" stroke-linecap="round"/>
  </g>
</svg>
'''
open(os.path.join(DEV, "icon.svg"), "w", encoding="utf-8", newline="\n").write(ICON)

print("ok ->", pkg["version"], "| size", len(src))
