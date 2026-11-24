# -*- coding: utf-8 -*-
"""快捷键注册兜底：键位冲突时 register 会抛错，不能让它带崩插件。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = r"E:\dsh\quick-input-dev\client.js"
src = open(CLIENT, encoding="utf-8").read()

old_head = """                const shortcuts = scoped.shortcuts
                if (!shortcuts || typeof shortcuts.register !== 'function') return () => {}
                return shortcuts.register({"""
new_head = """                const shortcuts = scoped.shortcuts
                if (!shortcuts || typeof shortcuts.register !== 'function') return () => {}
                try {
                  return shortcuts.register({"""
assert src.count(old_head) == 1
src = src.replace(old_head, new_head)

old_tail = """                  },
                })
              }, 'quick-input: shortcut')"""
new_tail = """                  },
                  })
                } catch (error) {
                  // 键位与别的命令冲突时 register 会抛错；快捷键没了不影响面板本身。
                  console.warn('[quick-input] 快捷键注册失败：', error)
                  return () => {}
                }
              }, 'quick-input: shortcut')"""
assert src.count(old_tail) == 1
src = src.replace(old_tail, new_tail)

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("ok, size =", len(src))
