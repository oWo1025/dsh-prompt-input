import difflib
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

a = open(
    r"C:\Users\LLC-Hdw\.dsh\profiles\desktop\node_modules\dsh-quick-input\client.js",
    encoding="utf-8",
).read().splitlines()
b = open(r"E:\dsh\quick-input-dev\client.js", encoding="utf-8").read().splitlines()

diff = list(difflib.unified_diff(a, b, lineterm="", n=0))
hunks = 0
added = removed = 0
for line in diff:
    if line.startswith("@@"):
        hunks += 1
        print(line)
    elif line.startswith("+") and not line.startswith("+++"):
        added += 1
    elif line.startswith("-") and not line.startswith("---"):
        removed += 1

print(f"\nhunks={hunks} +{added} -{removed}  (old {len(a)} lines -> new {len(b)} lines)")
