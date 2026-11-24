# -*- coding: utf-8 -*-
"""P1 收尾：字典、全局快捷键注册、版本 0.2.2。"""
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


sub("""        editCellShort: '✎ 点击可编辑',
      },""",
    """        editCellShort: '✎ 点击可编辑',
        previewMeta: '{page} · {n} 字',
        previewHint: '点击插入 · 拖动标题栏可移动位置',
        shortcutToggle: '打开 / 收起快捷输入',
      },""",
    "dict-zh")

sub("""        editCellShort: '✎ click to edit',
      },""",
    """        editCellShort: '✎ click to edit',
        previewMeta: '{page} · {n} chars',
        previewHint: 'Click to insert · drag the header to move',
        shortcutToggle: 'Toggle quick input',
      },""",
    "dict-en")

sub("""        announceBuild()
      },""",
    """        // 全局快捷键（可选服务）：Ctrl/Cmd+Shift+K 开合面板。
        // 用 ctx.inject 而不是 inject 数组，profile 里没有 shortcuts 时插件照常工作。
        try {
          if (typeof ctx.inject === 'function') {
            ctx.inject(['shortcuts'], (scoped) => {
              scoped.effect(() => {
                const shortcuts = scoped.shortcuts
                if (!shortcuts || typeof shortcuts.register !== 'function') return () => {}
                return shortcuts.register({
                  id: 'quick-input.toggle',
                  label: () => tr('shortcutToggle'),
                  aliases: ['quick input', 'quick phrases', 'prompt pad', '快捷输入'],
                  defaults: {
                    'desktop:macos': { code: 'KeyK', modifiers: ['primary', 'shift'] },
                    'desktop:windows': { code: 'KeyK', modifiers: ['primary', 'shift'] },
                    'desktop:linux': { code: 'KeyK', modifiers: ['primary', 'shift'] },
                    'web:macos': { code: 'KeyK', modifiers: ['primary', 'alt'] },
                    'web:windows': { code: 'KeyK', modifiers: ['primary', 'alt'] },
                    'web:linux': { code: 'KeyK', modifiers: ['primary', 'alt'] },
                  },
                  regions: ['page', 'editable'],
                  modals: [],
                  resolve: ({ modal }) => {
                    if (modal !== null && modal !== undefined) return { status: 'pass' }
                    const session = bridge.sessionId
                    if (session === null || session === undefined) return { status: 'pass' }
                    return {
                      status: 'handled',
                      run: () => {
                        const next = !isOpen(session)
                        store.open.set(session, next)
                        if (next) ensureDoc(false)
                        store.emit()
                      },
                    }
                  },
                })
              }, 'quick-input: shortcut')
            })
          }
        } catch {
          /* 没有快捷键服务就跳过，不影响面板 */
        }
        announceBuild()
      },""",
    "shortcut")

sub("const CLIENT_BUILD = '0.2.1+build1'", "const CLIENT_BUILD = '0.2.2+build1'", "build")

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)

i = os.path.join(DEV, "index.js")
s = open(i, encoding="utf-8").read()
assert s.count("const VERSION = '0.2.1'") == 1
open(i, "w", encoding="utf-8", newline="\n").write(s.replace("const VERSION = '0.2.1'", "const VERSION = '0.2.2'"))

p = os.path.join(DEV, "package.json")
pkg = json.load(open(p, encoding="utf-8"))
pkg["version"] = "0.2.2"
json.dump(pkg, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
open(p, "a", encoding="utf-8").write("\n")

print("ok ->", pkg["version"], "| size", len(src))
