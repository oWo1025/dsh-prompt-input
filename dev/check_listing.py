# -*- coding: utf-8 -*-
"""一键查「我的插件上架到哪一步了」。

用法：python dev/check_listing.py
退出码：0 = 已收录；1 = 还没收录

数据源统一用 raw.githubusercontent.com：cdn.jsdelivr.net 的 @main 有缓存
（2026-11-27 实测滞后了一整次合并），会给出假阴性。
"""
import io
import sys
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OWNER = "oWo1025"
REPO = "dsh-prompt-input"
SLUG = f"{OWNER}__{REPO}"
LIST = "awesome-dsh-plugin/awesome-dsh-plugin"
UA = {"User-Agent": "dsh-prompt-input/listing-check"}

CHECK = [
    ("① 条目文件是否已合并进列表主分支", f"https://raw.githubusercontent.com/{LIST}/main/data/plugins/{SLUG}.yml", "merge"),
    ("② 列表 README（英文）是否出现该条目", f"https://raw.githubusercontent.com/{LIST}/main/README.md", "en"),
    ("③ 列表 README（中文）是否出现该条目", f"https://raw.githubusercontent.com/{LIST}/main/README.zh.md", "zh"),
    ("④ 站点插件页（英文）", f"https://awesome-dsh-plugin.com/p/{OWNER}/{REPO}/", "http"),
    ("⑤ 站点插件页（中文）", f"https://awesome-dsh-plugin.com/zh/p/{OWNER}/{REPO}/", "http"),
    ("⑥ 我方 README", f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/README.md", "http"),
    ("⑦ 我方 icon-256.png", f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/icon-256.png", "http"),
    ("⑧ 我方 screenshots.json", f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/screenshots.json", "http"),
]

NEEDLE = f"](https://github.com/{OWNER}/{REPO})"


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.status, resp.read(4_000_000).decode("utf-8", "replace")


def main():
    listed = False
    print(f"检查 {OWNER}/{REPO}\n" + "=" * 64)

    for label, url, kind in CHECK:
        try:
            status, body = fetch(url)
        except urllib.error.HTTPError as e:
            print(f"{label}\n  ⬜ HTTP {e.code}")
            continue
        except Exception as e:  # noqa: BLE001
            print(f"{label}\n  ⚠️  {type(e).__name__}: {e}")
            continue

        if kind == "merge":
            listed = True
            print(f"{label}\n  ✅ 已在主分支（200）")
        elif kind in ("en", "zh"):
            hit = NEEDLE in body
            listed = listed or hit
            print(f"{label}\n  {'✅ 列表里已有这一行' if hit else '⬜ 还没有'}")
        else:
            print(f"{label}\n  {'✅ 200' if status == 200 else f'⬜ HTTP {status}'}")

    print("=" * 64)
    if listed:
        print("结论：已收录。")
        print(f"  站点页：https://awesome-dsh-plugin.com/p/{OWNER}/{REPO}/")
        print("  市场里搜索 prompt / 快捷输入 即可看到（索引缓存最长 10 分钟）。")
        return 0
    print("结论：还没收录。")
    print(f"  查看 PR：https://github.com/{LIST}/pulls?q=is%3Apr+author%3A{OWNER}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
