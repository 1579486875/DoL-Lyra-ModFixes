# -*- coding: utf-8 -*-
"""查 setup.props 的结构与 wearProp 取值方式。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== setup.props 相关 ===")
for mm in list(re.finditer(r"setup\.props", h))[:10]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 300):mm.start() + 400].replace("\n", " ")[:600]))

print("\n\n=== wearProp 函数开头（propErties 来源）===")
m = re.search(r"function wearProp\s*\(", h)
if m:
    print(h[m.start():m.start() + 1500])
else:
    m2 = re.search(r"window\.wearProp", h)
    if m2:
        print(h[max(0, m2.start() - 1600):m2.start() + 200])
