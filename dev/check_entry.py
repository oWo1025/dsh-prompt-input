import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"E:\dsh\dsh-prompt-input\docs\market-entry.yml"
text = open(P, encoding="utf-8").read()
print("bytes:", os.path.getsize(P), "| lines:", len(text.splitlines()))

QUOTES = ('"', "'")
problems = []
for i, line in enumerate(text.splitlines(), 1):
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if ": " not in stripped:
        continue
    key, _, value = stripped.partition(": ")
    if key.strip() in ("en", "zh", "description", "url", "name", "category", "icon"):
        if key.strip() in ("en", "zh"):
            quoted = value[:1] in QUOTES and value[-1:] in QUOTES
            print(f"  line {i:>2} [{key.strip()}] quoted={quoted}")
            if not quoted:
                problems.append(i)

print("未加引号的描述行:", problems or "无")
print("\n--- 内容 ---")
print(text)
