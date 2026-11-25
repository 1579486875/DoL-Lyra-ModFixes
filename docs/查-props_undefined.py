# -*- coding: utf-8 -*-
"""查 toothbrush / soap 的 props 配置，找 undefined 的来源。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
names = z.namelist()

# 1) props 路径模板
print("=== props 路径模板 ===")
for mm in list(re.finditer(r"clothes/props/", h))[:6]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 350):mm.start() + 350].replace("\n", " ")[:650]))

# 2) toothbrush / soap 的 ClothesItem 定义
print("\n\n=== toothbrush 定义 ===")
for mm in list(re.finditer(r'name:\s*"toothbrush"', h))[:2]:
    print("\n@%d:" % mm.start())
    print(h[max(0, mm.start() - 500):mm.start() + 1800].replace("\n", " ")[:2200])

# 3) 实际目录
print("\n\n=== props 目录实际结构 ===")
from collections import defaultdict
d = defaultdict(int)
for n in names:
    if "/img/clothes/props/" in n and n.endswith(".png"):
        rel = n.split("/img/clothes/props/")[1]
        parts = rel.split("/")
        d[parts[0] if len(parts) > 1 else "(根)"] += 1
for k, v in sorted(d.items()):
    print("  %-24s %d" % (k, v))
