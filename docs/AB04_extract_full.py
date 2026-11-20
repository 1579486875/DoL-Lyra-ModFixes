"""AB04：完整提取 201 处短英文短语 + 基线对比 + 分组。"""
import html as H
import json
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))

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
    if all(w.lower() in TECH for w in words):
        return False
    return True


def collect(t):
    out = Counter()
    for tag in ("span", "div", "i", "b", "small", "em", "strong"):
        for m in re.finditer(r"<" + tag + r"(?:\s[^>]*)?>([^<]{3,80})</" + tag + r">", t):
            v = m.group(1).strip()
            if is_en_phrase(v):
                out[v] += 1
    return out


cur = collect(g)
base = collect(gb)

print("=" * 95)
print(f"当前 {sum(cur.values())} 处 / {len(cur)} 种    基线 {sum(base.values())} 处 / {len(base)} 种")
print("=" * 95)

only_cur = {k: v for k, v in cur.items() if k not in base}
only_base = {k: v for k, v in base.items() if k not in cur}
print(f"\n只在当前（可能是我引入的）: {len(only_cur)}")
for k in list(only_cur)[:10]:
    print(f"    {k!r}")
print(f"\n只在基线（我修掉的）: {len(only_base)}")
for k in list(only_base)[:10]:
    print(f"    {k!r}")

print("\n" + "=" * 95)
print("当前全部英文短语（按字母序）")
print("=" * 95)
for k in sorted(cur):
    print(f"  {cur[k]:>2}×  {k!r}")

with open(r"E:\TAML\_dol\work\_short_en_full.json", "w", encoding="utf-8") as f:
    json.dump({k: v for k, v in cur.items()}, f, ensure_ascii=False, indent=1)
print(f"\n已保存 _short_en_full.json（{len(cur)} 种）")
