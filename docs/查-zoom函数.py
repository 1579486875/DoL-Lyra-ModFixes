# -*- coding: utf-8 -*-
"""查 zoom() 函数实现。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

for pat in (r"function zoom\s*\(", r"window\.zoom\s*=", r"zoom\s*=\s*function"):
    for mm in re.finditer(pat, h):
        print("=== %s @%d ===" % (pat, mm.start()))
        print(h[mm.start():mm.start() + 1200])
        print()
        break
