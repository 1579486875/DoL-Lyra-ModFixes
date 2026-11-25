# -*- coding: utf-8 -*-
"""确认 handheld / face 图层的 canvas 目标尺寸，决定统一到哪个规格。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== canvas 尺寸定义 ===")
for kw in ("canvas.width", "canvas.height", "CANVAS_W", "CANVAS_H", "512", "256"):
    pass

# 找 canvas 创建
for mm in list(re.finditer(r"createElement\(['\"]canvas['\"]\)", h))[:3]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 400):mm.start() + 600].replace("\n", " ")[:900]))

print("\n\n=== 找 width/height 常量 ===")
for mm in list(re.finditer(r"(?:width|WIDTH)\s*[:=]\s*(?:512|256|1024)", h))[:8]:
    print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 200):mm.start() + 200].replace("\n", " ")[:350]))

print("\n\n=== drawImage 调用（看是否带目标尺寸）===")
for mm in list(re.finditer(r"drawImage\(", h))[:5]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 300):mm.start() + 300].replace("\n", " ")[:560]))
