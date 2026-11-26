# -*- coding: utf-8 -*-
"""提取 setup.description_CN 的完整 _DESC 词表，检查 rugged/slight 等词是否覆盖。"""
import html as H
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

# 先反转义（这段是 <script> 里的，可能已经被 html.escape 过）
h2 = H.unescape(h) if "&lt;script&gt;" in h else h

for src, tag in ((h, "原样"), (h2, "反转义")):
    i = src.find("__descCNInstalled")
    if i < 0:
        continue
    print("=== 在【%s】里找到，位置 %d ===" % (tag, i))
    seg = src[i:i + 6000]
    print(seg[:5500])
    break
else:
    print("未找到 __descCNInstalled")
