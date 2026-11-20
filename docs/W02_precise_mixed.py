"""W02：精确扫「嵌在中文句子里的英文单词」。

三种精确形态：
  A. 中文 + 英文（紧邻，无空格）  → 如 她的skirt
  B. 中文 + 空格 + 英文 + 中文标点  → 如 她的 skirt，
  C. 英文 + 中文（紧邻）          → 如 skirt的
排除：变量名（_/. 紧邻）、camelCase、CSS 颜色、SugarCube 关键字
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

TECH = set("""
html css js png jpg jpeg gif svg webp json xml api url uri http https www
div span class id style href src img alt title type name value data
px em rem vh vw rgb rgba hex url base64 utf
npc pc rng hp xp mp mod mods modder modloader passage passages
sugarcube twine twee save load checkpoint debug error warning info log
true false null undefined color colour
gte gt lte lt isnot is eq neq and or not if else elseif
case switch default break continue return function var let const new this
cap worn lower upper text desc hint icon bottom top left right
purple gold green blue red pink orange white black grey gray teal
requiredValue displayName startPassage currentSexToyLeft currentSexToyRight
nStrings decimals var bool traits naked baby guard museum farm
arrow variable writing tentacle
""".split())


def is_tech(w):
    if w.lower() in TECH:
        return True
    if re.search(r"[A-Z]", w):                 # camelCase / PascalCase
        return True
    if len(w) < 4:
        return True
    return False


hits = []
PATTERNS = [
    ("A 中文+英文紧邻", re.compile(r"[\u4e00-\u9fff]([A-Za-z]{4,20})(?![A-Za-z_])")),
    ("B 中文+空格+英文+标点", re.compile(r"[\u4e00-\u9fff][  ]([A-Za-z]{4,20})\s*[,，。！？：；]")),
    ("C 英文+中文紧邻", re.compile(r"(?<![A-Za-z_])([A-Za-z]{4,20})[\u4e00-\u9fff]")),
]

for label, pat in PATTERNS:
    for m in pat.finditer(g):
        w = m.group(1)
        if is_tech(w):
            continue
        # 排除 HTML/JS 上下文
        pre = g[max(0, m.start() - 80):m.start()]
        if pre.rfind("<") > pre.rfind(">"):
            continue
        if pre and pre[-1] in ".=({[,;:+*/<>!&|?~^%$":
            continue
        hits.append((label, m.start(), w, g[max(0, m.start() - 70):m.start() + 80]))

print("=" * 95)
print(f"精确候选: {len(hits)} 处")
print("=" * 95)

cnt = Counter(h[2] for h in hits)
print("\n按词统计（去重，前 40）:")
for w, c in cnt.most_common(40):
    print(f"  {c:>3}  {w!r}")

print("\n" + "=" * 95)
print("明细（按词去重，前 40）")
print("=" * 95)
seen = set()
shown = 0
for label, pos, w, ctx in hits:
    if w in seen:
        continue
    seen.add(w)
    print(f"\n  [{w}]  {label}  @{pos}")
    print(f"    {ctx!r}")
    shown += 1
    if shown >= 40:
        break

with open(r"E:\TAML\_dol\work\_mixed2.json", "w", encoding="utf-8") as f:
    json.dump([{"kind": k, "pos": p, "word": w, "ctx": c} for k, p, w, c in hits[:800]],
              f, ensure_ascii=False, indent=1)
print(f"\n已保存 _mixed2.json（{len(hits)} 条）")
