# -*- coding: utf-8 -*-
"""查 home_relief 的触发条件，找出为什么会在公园触发。"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

print("=== core.js 里 home / 家 相关逻辑 ===")
for kw in ("home_relief", "isHome", "在家", "home"):
    hits = list(re.finditer(kw, s))
    if not hits:
        continue
    print("\n--- %s (%d 处) ---" % (kw, len(hits)))
    for mm in hits[:6]:
        print("@%d: %s" % (mm.start(), s[max(0, mm.start() - 350):mm.start() + 350].replace("\n", " ")[:700]))
        print()

print("\n\n=== text.twee 里 home_relief ===")
P2 = r"E:\TAML\_dol\work\联动模组\系统联动补全\twee\text.twee"
t = open(P2, encoding="utf-8").read()
i = t.find("home_relief")
while i >= 0:
    print("@%d: %s\n" % (i, t[max(0, i - 200):i + 400]))
    i = t.find("home_relief", i + 1)
