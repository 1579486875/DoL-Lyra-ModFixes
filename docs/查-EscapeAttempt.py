# -*- coding: utf-8 -*-
"""查 Escape Attempt 在 index 里的所有形态。"""
import re

h = open(r"E:\TAML\_dol\work\index_modded6.html", encoding="utf-8").read()

print("=== 原样搜索 ===")
for mm in list(re.finditer(r"Escape Attempt", h)):
    print("@%d: %s" % (mm.start(), h[max(0, mm.start() - 150):mm.start() + 100].replace("\n", " ")[:280]))

print("\n=== 转义形态 &amp;quot; 等 ===")
for pat in (r'note\s+&quot;Escape Attempt&quot;', r'note\s+"Escape Attempt"', r"note\s+&#34;Escape Attempt&#34;"):
    n = len(re.findall(pat, h))
    print("  %-40s %d" % (pat, n))

print("\n=== 统计 ===")
print("  Escape Attempt 总数:", len(re.findall(r"Escape Attempt", h)))

# 看一处完整上下文
i = h.find("Escape Attempt")
if i > 0:
    print("\n=== 第一处完整上下文 ===")
    print(h[max(0, i - 600):i + 400])
