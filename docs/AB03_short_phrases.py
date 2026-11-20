"""AB03：扫 <span>/<div> 里的短英文短语（2-4 词）。

之前的扫描只抓「整句英文」（有句末标点、4+ 词），漏掉了：
  - 2-3 词的短语（如 "Very fast" / "Not now"）
  - 标签内嵌的短文本
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

TECH = set("""
html css js png jpg gif svg webp json xml api url http https div span class id style
px em rem vh vw rgb rgba hex base64 npc pc rng hp xp mod passage sugarcube twine twee
save load debug error warning info log true false null undefined color colour
black white red blue green yellow purple orange pink grey gray gold teal brown cyan
left right top bottom center middle none auto normal bold italic underline
small large medium big tiny huge
""".split())


def is_en_phrase(s):
    s = s.strip()
    if not s or len(s) < 3 or len(s) > 60:
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    if s.startswith("<") or re.search(r"[${}()\[\];=<>`]", s):
        return False
    words = re.findall(r"[A-Za-z]{2,}", s)
    if len(words) < 2:
        return False
    # 全部词都是技术词 → 排除
    if all(w.lower() in TECH for w in words):
        return False
    return True


print("=" * 95)
print("1. <span>/<div>/<i>/<b> 标签内纯英文（2-4 词）")
print("=" * 95)
n1 = 0
hits = []
for tag in ("span", "div", "i", "b", "small", "em", "strong"):
    for m in re.finditer(r"<" + tag + r"(?:\s[^>]*)?>([^<]{3,80})</" + tag + r">", g):
        v = m.group(1)
        if is_en_phrase(v):
            n1 += 1
            if len(hits) < 40:
                hits.append((tag, v.strip(), g[max(0, m.start() - 60):m.start() + 110]))

print(f"  共 {n1} 处")
seen = set()
shown = 0
for tag, v, ctx in hits:
    if v in seen:
        continue
    seen.add(v)
    print(f"  [{tag}] {v!r}")
    shown += 1
    if shown >= 30:
        break

print("\n" + "=" * 95)
print("2. 按内容统计（去重）")
print("=" * 95)
c = Counter(h[1] for h in hits)
for v, n in c.most_common(30):
    print(f"  {n:>2}×  {v!r}")

print("\n" + "=" * 95)
print("3. 对比基线：这些在基线里也有吗")
print("=" * 95)
import zipfile
gb = H.unescape(zipfile.ZipFile(
    r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
).read("assets/www/index.html").decode("utf-8", "replace"))

n_b = 0
for tag in ("span", "div", "i", "b", "small", "em", "strong"):
    for m in re.finditer(r"<" + tag + r"(?:\s[^>]*)?>([^<]{3,80})</" + tag + r">", gb):
        if is_en_phrase(m.group(1)):
            n_b += 1
print(f"  基线: {n_b} 处 / 当前: {n1} 处  差异: {n1 - n_b:+d}")

with open(r"E:\TAML\_dol\work\_short_en_phrases.json", "w", encoding="utf-8") as f:
    json.dump([{"tag": t, "text": v} for t, v, _ in hits], f, ensure_ascii=False, indent=1)
print("\n已保存 _short_en_phrases.json")
