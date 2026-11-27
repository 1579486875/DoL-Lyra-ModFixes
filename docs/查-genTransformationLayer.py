# -*- coding: utf-8 -*-
"""查 genTransformationLayer 的 canvas 尺寸，判定 1024x256 是否会错位。"""
import html as H
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== genTransformationLayer 定义 ===")
m = re.search(r"genTransformationLayer\s*[(:=]", h)
if m:
    print(h[m.start():m.start() + 3000])
else:
    print("未找到，搜 genTransformation")

print("\n\n=== 搜 transformations 路径构造 ===")
for mm in list(re.finditer(r"body/transformations", h))[:5]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 700):mm.start() + 500]))
