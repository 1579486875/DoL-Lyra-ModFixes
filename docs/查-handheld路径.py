# -*- coding: utf-8 -*-
"""找 handheld/props 图层的路径拼接，定位 undefined。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== 所有 props/ 路径模板 ===")
for mm in re.finditer(r"props/\$\{|props/\" *\+|props/' *\+", h):
    seg = h[max(0, mm.start() - 400):mm.start() + 300]
    print("\n@%d:" % mm.start())
    print(seg.replace("\n", " ")[:650])

print("\n\n=== wearProp 宏定义 ===")
m = re.search(r"<<widget \"wearProp\">>", h)
if m:
    print(h[m.start():m.start() + 1500])
else:
    m2 = re.search(r"wearProp", h)
    if m2:
        print(h[max(0, m2.start() - 300):m2.start() + 700].replace("\n", " ")[:900])

print("\n\n=== handheld 图层定义 ===")
for mm in list(re.finditer(r'"handheld"', h))[:5]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 300):mm.start() + 700].replace("\n", " ")[:950]))
