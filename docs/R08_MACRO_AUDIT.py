# -*- coding: utf-8 -*-
"""第8轮：宏结构配对 + 常见空指针模式扫描。"""
import html as H
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PS[m.group(1)] = m.group(2)

print("passages:", len(PS))

# 1) <<if>> / <</if>> 配对
bad_if = []
bad_for = []
bad_link = []
for name, body in PS.items():
    o = len(re.findall(r"<<if\b", body))
    c = len(re.findall(r"<</if>>", body))
    if o != c:
        bad_if.append((name, o, c))
    o2 = len(re.findall(r"<<for\b", body))
    c2 = len(re.findall(r"<</for>>", body))
    if o2 != c2:
        bad_for.append((name, o2, c2))
    o3 = len(re.findall(r"<<link\b", body))
    c3 = len(re.findall(r"<</link>>", body))
    if o3 != c3:
        bad_link.append((name, o3, c3))

print("\nif 配对异常:", len(bad_if))
for n, o, c in bad_if[:10]:
    print("  %-44s if=%d /if=%d" % (n, o, c))
print("for 配对异常:", len(bad_for))
for n, o, c in bad_for[:10]:
    print("  %-44s for=%d /for=%d" % (n, o, c))
print("link 配对异常:", len(bad_link))
for n, o, c in bad_link[:10]:
    print("  %-44s link=%d /link=%d" % (n, o, c))

# 2) 常见空指针模式
print("\n=== 空指针模式 ===")
PATTERNS = [
    (r"\.\w+\.\w+\.\w+\s*>>", "三级链式访问"),
    (r"\$NPCList\[\$?\w+\]\.\w+", "NPCList 直接访问"),
]
for pat, label in PATTERNS:
    c = len(re.findall(pat, g))
    print("  %-18s %d" % (label, c))
