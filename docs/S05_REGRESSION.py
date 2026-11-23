# -*- coding: utf-8 -*-
"""第5轮：复查之前修过的英文残留是否复发。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

CHECKS = {
    "_exercise 英文赋值": r'set _exercise to "[a-z]',
    "_hand 英文常量": r'set _hand to "(?:right|left)"',
    "fish 错译": r"\|fish,海星\||^fish,海星",
    "glory 未翻": r'"glory(?:hole)?": " Glory Hole"',
    "title 缺失(alpha)": r'"alpha"',
}

print("=== 历史修复防复发 ===")
for label, pat in CHECKS.items():
    n = len(re.findall(pat, g, re.M))
    flag = "OK" if n == 0 else "⚠ %d 处" % n
    print("  %-22s %s" % (label, flag))

print("\n=== BODYPARTS 参数分布 ===")
from collections import Counter
c = Counter()
for m in re.finditer(r"setup\.BODYPARTS_CN_NAME\(([^)]{1,50})\)", g):
    arg = m.group(1).strip()
    c[arg] += 1
for k, v in c.most_common(15):
    print("  %-28s %d" % (k, v))

print("\n=== NPC_CN_TYPE 参数分布（前 10）===")
c2 = Counter()
for m in re.finditer(r"setup\.NPC_CN_TYPE\(([^)]{1,50})\)", g):
    c2[m.group(1).strip()] += 1
for k, v in c2.most_common(10):
    print("  %-28s %d" % (k, v))
