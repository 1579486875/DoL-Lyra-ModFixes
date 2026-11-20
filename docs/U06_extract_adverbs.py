"""U06：完整提取「裸英文副词」（<<if>> 分支里只有英文单词）。"""
import html as H
import json
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PAT = re.compile(r"<<(if|elseif|else)\b[^>]*>>\s*\n\s*([A-Za-z][A-Za-z\- ']{1,40})\s*\n\s*<<", re.M)

hits = []
for m in PAT.finditer(g):
    w = m.group(2).strip()
    if not w:
        continue
    if re.search(r"[\u4e00-\u9fff]", w):
        continue
    if w.startswith("<<") or w.startswith("<"):
        continue
    # 必须是「词」而不是代码
    if re.search(r"[${}()\[\];=]", w):
        continue
    hits.append({
        "pos": m.start(),
        "word": w,
        "ctx": g[max(0, m.start() - 100):m.start() + 160],
    })

print(f"共 {len(hits)} 处\n")

# 按词去重统计
from collections import Counter, defaultdict
cnt = Counter(h["word"] for h in hits)
print("=" * 95)
print("按词统计（去重）")
print("=" * 95)
for w, c in cnt.most_common():
    print(f"  {c:>3}  {w!r}")

print("\n" + "=" * 95)
print("逐条明细")
print("=" * 95)
by_word = defaultdict(list)
for h in hits:
    by_word[h["word"]].append(h)

for w in sorted(by_word):
    hs = by_word[w]
    print(f"\n[{w}]  {len(hs)} 处")
    for h in hs[:3]:
        print(f"  @{h['pos']}")
        print(f"  {h['ctx']!r}")

with open(r"E:\TAML\_dol\work\_bare_en_adverbs.json", "w", encoding="utf-8") as f:
    json.dump(hits, f, ensure_ascii=False, indent=1)
print(f"\n已保存 _bare_en_adverbs.json（{len(hits)} 条）")
