# -*- coding: utf-8 -*-
"""一键查「我的插件上架到哪一步了」。

用法：python dev/check_listing.py
退出码：0 = 已收录；1 = 还没收录（或正在审核）
"""
import io
import sys
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OWNER = "oWo1025"
REPO = "dsh-prompt-input"
SLUG = f"{OWNER}__{REPO}"
UA = {"User-Agent": "dsh-prompt-input/listing-check"}

CHECKS = [
    (
        "① 条目文件是否已合并进列表主分支",
        f"https://cdn.jsdelivr.net/gh/awesome-dsh-plugin/awesome-dsh-plugin@main/data/plugins/{SLUG}.yml",
    ),
    (
        "② 站点是否已有插件详情页",
        f"https://awesome-dsh-plugin.com/p/{OWNER}/{REPO}/",
    ),
    (
        "③ 列表 README（英文）里是否出现该条目",
        "https://cdn.jsdelivr.net/gh/awesome-dsh-plugin/awesome-dsh-plugin@main/README.md",
    ),
    ("④ 我方仓库 README 是否可达", f"https://cdn.jsdelivr.net/gh/{OWNER}/{REPO}@main/README.md"),
    ("⑤ 我方图标 icon-256.png 是否可达", f"https://cdn.jsdelivr.net/gh/{OWNER}/{REPO}@main/icon-256.png"),
    ("⑥ 我方 screenshots.json 是否可达", f"https://cdn.jsdelivr.net/gh/{OWNER}/{REPO}@main/screenshots.json"),
]


def fetch(url, limit=400_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, resp.read(limit).decode("utf-8", "replace")


def main():
    listed = False
    print(f"检查 {OWNER}/{REPO}\n" + "=" * 62)

    for idx, (label, url) in enumerate(CHECKS):
        try:
            status, body = fetch(url)
        except urllib.error.HTTPError as e:
            status, body = e.code, ""
        except Exception as e:  # noqa: BLE001 - 网络异常也要给出一行结论
            print(f"{label}\n  ⚠️  网络错误：{type(e).__name__}: {e}")
            continue

        if idx == 2:
            hit = f"](https://github.com/{OWNER}/{REPO})" in body
            print(f"{label}\n  {'✅ README 中已出现' if hit else '⬜ README 中还没有'}")
            listed = listed or hit
            continue

        ok = status == 200
        if idx in (0, 1):
            listed = listed or ok
        print(f"{label}\n  {'✅ 200' if ok else f'⬜ HTTP {status}'}  {url if not ok else ''}".rstrip())

    print("=" * 62)
    if listed:
        print("结论：已收录（或已合并，等下一次目录重建）。")
        return 0
    print("结论：还没收录。这通常意味着 PR 尚未合并，属于正常等待阶段。")
    print(f"  查看 PR：https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/pulls?q=is%3Apr+author%3A{OWNER}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
