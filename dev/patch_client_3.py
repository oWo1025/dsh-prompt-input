# -*- coding: utf-8 -*-
"""P0 第三步：气泡语义修正——开合只记在会话内，不跨刷新自动展开。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = r"E:\dsh\quick-input-dev\client.js"
src = open(CLIENT, encoding="utf-8").read()

start = "    // ------------------------------------------------------------ 常驻开关的记忆"
end = "    // ------------------------------------------------------------ 模块级共享状态"
assert src.count(start) == 1 and src.count(end) == 1
a, b = src.index(start), src.index(end)
assert a < b

NEW = """    // ------------------------------------------------------------ 开合状态

    /**
     * 气泡只在本次会话里记住开合：刷新页面/重开应用一律收起。
     * （旧版是「常驻面板」，会把这个状态写进 localStorage；气泡形态不这么做——
     *   刷新后自动弹出一个浮层是打扰，而不是恢复。）
     */
    function isOpen(sessionId) {
      return store.open.get(sessionId) === true
    }

"""
src = src[:a] + NEW + src[b:]

# 清掉两处写入常驻开关的调用（函数已删）
old_toggle = """              store.open.set(sessionId, next)
              writeOpenFlag(next)
              if (next) ensureDoc(false)"""
new_toggle = """              store.open.set(sessionId, next)
              if (next) ensureDoc(false)"""
assert src.count(old_toggle) == 1
src = src.replace(old_toggle, new_toggle)

old_close = """      store.flash.delete(sessionId)
      writeOpenFlag(false)
      store.emit()"""
new_close = """      store.flash.delete(sessionId)
      store.emit()"""
assert src.count(old_close) == 1
src = src.replace(old_close, new_close)

assert "writeOpenFlag" not in src, "stale writeOpenFlag reference"
assert "readOpenFlag" not in src, "stale readOpenFlag reference"

open(CLIENT, "w", encoding="utf-8", newline="\n").write(src)
print("patched, size =", len(src))
