"""W01（第5轮）：扫「中英混杂」句子 —— 中文叙述里夹英文单词。

上一轮修了 1 处（"The " + _person + " 掀起 " + _his + " skirt, "），同类可能还有。

判据加强（对比 V01 的松判据）：
  1. 英文词 ≥3 字母
  2. 排除技术词表
  3. 上下文必须是「叙述性文本」（前后有中文标点或连续中文）
  4. 排除 HTML 标签属性、CSS、JS
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

# 技术词黑名单（这些出现是正常的）
TECH = set("""
html css js png jpg jpeg gif svg webp json xml api url uri http https www
div span class id style href src img alt title type name value data
px em rem vh vw rgb rgba hex url base64 utf
npc pc rng hp xp mp
mod mods modder modloader passage passages
sugarcube twine twee save load
checkpoint debug error warning info log
true false null undefined
color colour
""" .split())

# 叙述性上下文：前后 30 字符内有中文
def is_narrative(s_full, w_start, w_end):
    pre = s_full[max(0, w_start - 30):w_start]
    post = s_full[w_end:w_end + 30]
    n_cn = len(re.findall(r"[\u4e00-\u9fff]", pre + post))
    return n_cn >= 2


hits = []
for m in re.finditer(r"[A-Za-z]{3,20}", g):
    w = m.group(0)
    if w.lower() in TECH:
        continue
    # 排除 HTML 标签内 / 属性值内
    pre = g[max(0, m.start() - 120):m.start()]
    # 找到最近的 < 和 >
    lt = pre.rfind("<")
    gt = pre.rfind(">")
    if lt > gt:      # 在标签内
        continue
    # 排除 JS 上下文（前面有 . = ( , [ 等代码符号紧邻）
    if pre and pre[-1] in ".=({[,;:+*/<>!&|?~^%":
        continue
    if m.end() < len(g) and g[m.end()] in ".=({[,;:+*/<>!&|?~^%)":
        # 但要排除句子里的句号 —— 只排除明显是代码的
        if g[m.end()] not in ".':":
            continue
    if not is_narrative(g, m.start(), m.end()):
        continue
    hits.append((m.start(), w, g[max(0, m.start() - 60):m.start() + 70]))

print("=" * 95)
print(f"中英混杂候选: {len(hits)} 处")
print("=" * 95)

cnt = Counter(h[1] for h in hits)
print("\n按词统计（前 40）:")
for w, c in cnt.most_common(40):
    print(f"  {c:>3}  {w!r}")

print("\n" + "=" * 95)
print("明细（前 40，去重按词）")
print("=" * 95)
seen = set()
shown = 0
for pos, w, ctx in hits:
    if w in seen:
        continue
    seen.add(w)
    print(f"\n  [{w}]  @{pos}")
    print(f"    {ctx!r}")
    shown += 1
    if shown >= 40:
        break

with open(r"E:\TAML\_dol\work\_mixed_cn_en.json", "w", encoding="utf-8") as f:
    json.dump([{"pos": p, "word": w, "ctx": c} for p, w, c in hits[:500]],
              f, ensure_ascii=False, indent=1)
print(f"\n已保存 _mixed_cn_en.json（{len(hits)} 条）")
