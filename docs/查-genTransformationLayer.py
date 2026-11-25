# -*- coding: utf-8 -*-
"""查 PlayerCanvasHelper.genTransformationLayer 的实现。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

m = re.search(r"static genTransformationLayer\s*\(", h)
if not m:
    m = re.search(r"genTransformationLayer\s*\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)\s*\{", h)
if not m:
    print("❌ 未找到")
    raise SystemExit(0)

print("=== genTransformationLayer 定义 @%d ===" % m.start())
print(h[m.start():m.start() + 1800])
