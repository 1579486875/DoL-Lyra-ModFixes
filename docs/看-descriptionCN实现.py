# -*- coding: utf-8 -*-
"""看 description_CN 函数的实际查找逻辑（词表之后）。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

i = h.find('"thick": "丰腴"')
if i < 0:
    i = h.find("__descCNInstalled")
print("=== 词表之后（函数实现）===")
print(h[i:i + 2500])
