"""第 42 轮：修原版 bug <<set $bus "avery_garage">> + 查 $sexRitual.bondage 那处。"""
import html
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("$sexRitual.bondage 的可疑表达式")
print("=" * 94)
n = 0
for m in re.finditer(r"<<=\s*\$sexRitual\.bondage\s", g):
    n += 1
    seg = g[max(0, m.start() - 80):m.start() + 400]
    print(f"\n@{m.start()}: {seg!r}")
print(f"\n共 {n} 处")

print("\n" + "=" * 94)
print("所有 <<= 里含 ' ? : ' 的（缺条件的）")
print("=" * 94)
cnt = 0
for m in re.finditer(r"<<=\s", g):
    i = m.end()
    depth = 1
    while i < len(g) and depth > 0:
        if g.startswith("<<", i):
            depth += 1
            i += 2
        elif g.startswith(">>", i):
            depth -= 1
            i += 2
        else:
            i += 1
    expr = g[m.end():i - 2]
    # 形如 X "..." ? : "..."  —— 条件位置是字符串
    if re.search(r'"\s*\?\s*:', expr):
        cnt += 1
        print(f"\n  @{m.start()}: {expr[:200]!r}")
        print(f"      原文: {g[max(0,m.start()-60):m.start()+280]!r}")
print(f"\n共 {cnt} 处")
