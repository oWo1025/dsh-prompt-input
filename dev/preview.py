# -*- coding: utf-8 -*-
"""把 client.js 里的 CSS 抽出来，做一个静态预览（只为看布局，不是替代真机验证）。"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLIENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'client.js')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preview.html')

src = open(CLIENT, encoding="utf-8").read()
m = re.search(r"const CSS = `(.*?)`\n", src, re.S)
assert m, "css block not found"
css = m.group(1)

TOKENS = """
:root{
  --dsw-alias-bg-layer-2:#ffffff;
  --dsw-alias-bg-module-platform:#f2f4f7;
  --dsw-alias-bg-layer-1:#ffffff;
  --dsw-alias-bg-overlay:#eef0f3;
  --dsw-alias-label-primary:#1f2328;
  --dsw-alias-label-secondary:#667085;
  --dsw-alias-label-caption:#98a2b3;
  --dsw-alias-border-l1:rgba(0,0,0,.06);
  --dsw-alias-border-l2:rgba(0,0,0,.12);
  --dsw-alias-border-selected:#4d6bfe;
  --dsw-alias-brand-primary:#4d6bfe;
  --dsw-alias-interactive-bg-hover:rgba(16,24,40,.06);
  --dsw-alias-state-success-primary:#12b76a;
  --dsw-alias-state-error-primary:#d92d20;
  --dsw-radius-sm:8px; --dsw-radius-md:12px; --dsw-radius-lg:16px;
  --dsw-elevation-panel:0 12px 32px rgba(16,24,40,.14), 0 2px 6px rgba(16,24,40,.06);
}
body{margin:0;background:#f7f8fa;font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:#1f2328}
.stage{display:flex;flex-wrap:wrap;gap:32px;padding:28px;align-items:flex-start;box-sizing:border-box}
.slot{position:relative;width:440px;display:flex;flex-direction:column;gap:10px}
.host{height:98px;border:1px solid rgba(0,0,0,.08);border-radius:16px;background:#fff;display:flex;align-items:flex-end;padding:10px;gap:8px;color:#98a2b3;font-size:12px}
.host .fake-btn{width:28px;height:28px;border-radius:999px;background:#f2f4f7;display:grid;place-items:center;color:#667085}
.dsq-pop{position:static !important;width:420px}
.caption{font-size:12px;color:#98a2b3;margin:0}
"""

CARDS9 = [
    "苏格拉底问诊", "双层解释", "反向拆解", "横纵分析", "事实核查",
    "别给通用建议", "专家会诊", "第一性原理", "跨领域借解",
]


def grid(names, edit=False, hover=None):
    cells = []
    for i, name in enumerate(names):
        sub = '<span class="dsq-card-sub">✎ 点击可编辑</span>' if edit else ''
        cls = "dsq-card dsq-card-hover" if hover == i else "dsq-card"
        cells.append(f'<button class="{cls}"><span class="dsq-card-label">{name}</span>{sub}</button>')
    if edit:
        for _ in range(9 - len(names)):
            cells.append('<button class="dsq-card dsq-card-empty">＋</button>')
    return '<div class="dsq-grid3" role="group">' + "".join(cells) + "</div>"


def popover(title, names, active=0, query="", results=None, overflow=False, empty=False, hover=None):
    if results is not None:
        body = '<div class="dsq-results" role="listbox">' + "".join(
            f'<button class="dsq-item{" dsq-item-on" if i == 0 else ""}">'
            f'<span class="dsq-item-label">{r[0]}</span>'
            f'<span class="dsq-item-snippet">{r[1]}</span>'
            f'<span class="dsq-item-page">{r[2]}</span></button>'
            for i, r in enumerate(results)
        ) + "</div>"
    elif empty:
        body = (
            '<div class="dsq-empty">'
            '<div class="dsq-empty-title">这一页还空着</div>'
            "<div>点底部的铅笔按钮添加第一条</div></div>"
        )
    else:
        body = grid(names, hover=hover)

    tab_names = ["常用", "代码", "问清·学", "解题·决", "指挥①", "指挥②"]
    if overflow:
        tab_names = ["最近"] + tab_names + ["第 7 页"]
    tabs = "".join(
        f'<button class="dsq-tab{" dsq-tab-on" if i == active else ""}">{t}</button>'
        for i, t in enumerate(tab_names)
    )
    tabs_cls = "dsq-tabs dsq-tabs-scroll" if overflow else "dsq-tabs"
    arrow_l = '<button class="dsq-mini">‹</button>' if overflow else ""
    arrow_r = '<button class="dsq-mini">›</button>' if overflow else ""
    total = len(tab_names)
    return f"""
    <div class="slot">
      <div class="caption">{title}</div>
      <div class="host"><span class="fake-btn">
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" aria-hidden="true">
          <g transform="rotate(-9 9.5 5.2)"><rect x="4.6" y="1.4" width="9.2" height="6.4" rx="1.8" stroke-width="1.3" opacity=".42"/></g>
          <rect x="1.7" y="6.4" width="9.5" height="6.6" rx="1.9" stroke-width="1.3"/>
          <path d="M4 9.2h4.4M4 11.3h2.8" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
      </span><span>输入你的消息…</span></div>
      <div class="dsq-pop" role="dialog">
        <div class="dsq-head">
          <div class="dsq-grip" title="拖动这里移动面板（双击复位）" aria-hidden="true">
            <svg width="10" height="14" viewBox="0 0 10 14" fill="currentColor"><circle cx="2" cy="2" r="1.5"/><circle cx="7" cy="2" r="1.5"/><circle cx="2" cy="7" r="1.5"/><circle cx="7" cy="7" r="1.5"/><circle cx="2" cy="12" r="1.5"/><circle cx="7" cy="12" r="1.5"/></svg>
          </div>
          <div class="dsq-searchwrap">
            <svg class="dsq-searchicon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
            <input class="dsq-search" type="search" value="{query}" placeholder="搜索 Prompt…">
          </div>
          <button class="dsq-x"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
        </div>
        <div class="dsq-body">{body}</div>
        <div class="dsq-tabsrow">
          {arrow_l}
          <div class="{tabs_cls}" role="tablist">{tabs}</div>
          {arrow_r}
          <span class="dsq-count">{active + 1}/{total}</span>
          <button class="dsq-mini"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4L18.5 9.5a2.8 2.8 0 0 0-4-4L4 16v4z"/><path d="M13.5 6.5l4 4"/></svg></button>
        </div>
      </div>
    </div>"""


RESULTS = [
    ("苏格拉底问诊", "我的困惑是：【尽量具体地描述发生了什么、你怎么理解，以及你卡在哪里】。", "问清·学"),
    ("双向钢人论证", "先别急着回答，也别默认我已经把问题想清楚。", "解题·决"),
    ("事实核查", "我要核查的说法是：【粘贴观点、结论、数据或方案】。", "问清·学"),
]

MEASURE_JS = """
const lines = [];
document.querySelectorAll('.dsq-pop').forEach(function (pop, i) {
  var row = pop.querySelector('.dsq-tabsrow');
  var tabs = row.querySelector('.dsq-tabs');
  var count = row.querySelector('.dsq-count');
  var mini = row.querySelector('.dsq-mini');
  lines.push('#' + i
    + ' pop=' + pop.clientWidth + 'x' + pop.offsetHeight
    + ' bodyH=' + pop.querySelector('.dsq-body').offsetHeight
    + ' row=' + row.clientWidth
    + ' cssW=' + getComputedStyle(row).width
    + ' tabs=' + tabs.clientWidth
    + ' scroll=' + tabs.scrollWidth
    + ' count=' + count.clientWidth
    + ' mini=' + (mini ? mini.clientWidth : '-'));
});
lines.push('body=' + document.body.clientWidth);
document.getElementById('measure').textContent = lines.join('\\n');
"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>quick-input 预览</title>
<style>{TOKENS}
{css}
#measure{{position:fixed;right:8px;bottom:8px;z-index:99;background:#111;color:#fff;font:11px/1.5 monospace;padding:8px;border-radius:8px;white-space:pre}}
/* 预览专用：复刻 .dsq-card:hover 的三条声明，用来验证上移和阴影不会被裁 */
.dsq-card-hover{{transform:translateY(-1px);border-color:color-mix(in srgb,#4d6bfe 24%,rgba(0,0,0,.16));box-shadow:0 6px 16px -10px color-mix(in srgb,#4d6bfe 55%,transparent)}}
</style></head>
<body><div class="stage">
{popover("A · 9 格页（第一行第 1 张模拟悬停）", CARDS9, active=0, hover=0)}
{popover("B · 2 格页（内容少，应与 A 等高）", ["继续", "先给结论"], active=1)}
{popover("C · 搜索态", [], active=0, query="苏格拉底", results=RESULTS)}
{popover("D · 8 个页签（溢出，左右翻页 + 两端渐隐）", CARDS9, active=2, overflow=True)}
{popover("E · 空页", [], empty=True)}
</div>
<div class="dsq-preview" style="left:640px;top:545px;width:300px">
  <div class="dsq-preview-title">苏格拉底问诊</div>
  <div class="dsq-preview-meta">问清·学 · 396 字</div>
  <div class="dsq-preview-text">我的困惑是：【尽量具体地描述发生了什么、你怎么理解，以及你卡在哪里】。

先不要给建议。请对我进行一次苏格拉底式问诊，通过最多6个问题，帮我找到真正值得回答的问题。

请遵守这些规则：
1. 每次只问一个问题，根据我的回答决定下一问，不要提前给我一整套问卷；
2. 优先区分我说的是可验证的事实、对事实的解释、价值判断，还是我希望实现的目标；</div>
  <div class="dsq-preview-foot">点击插入 · 拖动标题栏可移动位置</div>
</div>
<pre id="measure"></pre>
<script>{MEASURE_JS}</script>
</body></html>
"""

open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, len(html), "chars, css", len(css))
