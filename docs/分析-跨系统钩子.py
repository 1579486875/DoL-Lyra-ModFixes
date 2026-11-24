# -*- coding: utf-8 -*-
"""找出所有跨系统钩子 widget，以及需求系统与暴露/服装/战斗的交叉。"""
import html as H
import re
from collections import defaultdict

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))
PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PS[m.group(1)] = m.group(2)

# 1) swim_strip_check 实现
print("=== swim_strip_check ===")
for nm in PS:
    if "swim_strip_check" in nm or "swim" in nm.lower() and "widget" in nm.lower():
        print("  passage:", nm)
m = re.search(r'<<widget\s+"swim_strip_check"[^>]*>>(.*?)<</widget>>', g, re.S)
if m:
    print(m.group(1)[:1200])
else:
    print("  未找到 widget 定义，搜引用:")
    for mm in list(re.finditer(r"swim_strip_check", g))[:5]:
        print("   ", repr(g[max(0, mm.start() - 200):mm.start() + 200])[:400])

# 2) 需求系统相关钩子
print("\n=== 与 BasicNeeds 交互的 widget/passage ===")
for kw in ("bnSettle", "bnMood", "BasicNeeds", "bladder", "digest"):
    hits = [(nm, b) for nm, b in PS.items() if kw in b]
    print("  %-14s %d 个 passage: %s" % (kw, len(hits), [h[0] for h in hits[:6]]))

# 3) 暴露度触发点
print("\n=== 触发暴露的宏/函数 ===")
for kw in ("<<exhibitionist", "<<exhibitionism", "exposedUsed", "fame.exhibitionism"):
    n = len(re.findall(re.escape(kw), g))
    print("  %-22s %d 次" % (kw, n))

# 4) 战斗 -> 怀孕
print("\n=== 战斗中触发怀孕 ===")
for kw in ("impregnat", "pregnancyChance", "getPregnant", "knotted"):
    n = len(re.findall(kw, g))
    print("  %-22s %d 次" % (kw, n))

# 5) 需求 -> 事件
print("\n=== 需求触发的随机事件 ===")
for kw in ("bnEvent", "needEvent", "toiletEvent", "wetSelf", "soiledSelf"):
    n = len(re.findall(kw, g))
    print("  %-22s %d 次" % (kw, n))
