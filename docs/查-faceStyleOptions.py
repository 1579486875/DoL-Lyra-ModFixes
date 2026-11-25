# -*- coding: utf-8 -*-
"""查 faceStyleOptions / cheatsFaceStyle / facevariant 的 textMap。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== setup.faceStyleOptions 定义 ===")
for mm in re.finditer(r"faceStyleOptions\s*[:=]", h):
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 300):mm.start() + 500].replace("\n", " ")[:800]))

print("\n\n=== cheatsFaceStyle widget ===")
for mm in re.finditer(r'<<widget "cheatsFaceStyle">>', h):
    print("\n@%d: %s" % (mm.start(), h[mm.start():mm.start() + 900].replace("\n", " ")[:900]))

print("\n\n=== facevariant textMap（举止）===")
for mm in re.finditer(r"facevariant", h):
    seg = h[max(0, mm.start() - 100):mm.start() + 700]
    if "textMap" in seg:
        print("\n@%d: %s" % (mm.start(), seg.replace("\n", " ")[:800]))
        break

print("\n\n=== 搜 Makeup 作为 facevariant 值 ===")
for mm in list(re.finditer(r'["\']?makeup["\']?', h, re.I))[:10]:
    seg = h[max(0, mm.start() - 200):mm.start() + 200]
    if "facevariant" in seg or "posture" in seg or "举止" in seg:
        print("\n@%d: %s" % (mm.start(), seg.replace("\n", " ")[:400]))
