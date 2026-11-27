# -*- coding: utf-8 -*-
"""查 ModelLayers 系统的 canvas 尺寸是怎么定的（固定值 vs 自适应图片）。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== 1) canvas.width 赋值处 ===")
for mm in list(re.finditer(r"\.width\s*=\s*", h))[:40]:
    seg = h[max(0, mm.start() - 120):mm.start() + 120].replace("\n", " ")
    if "canvas" in seg.lower() or "Canvas" in seg:
        print("  @%d: %s" % (mm.start(), seg[:240]))

print("\n\n=== 2) ModelLayers / BaseCanvas 的尺寸逻辑 ===")
for kw in ("class BaseCanvas", "BaseCanvas = class", "new BaseCanvas", "class ModelLayers", "ModelLayers"):
    m = re.search(re.escape(kw), h)
    if m:
        print("\n--- %s @%d ---" % (kw, m.start()))
        print(h[max(0, m.start() - 200):m.start() + 1200])
        break

print("\n\n=== 3) drawImage 带尺寸参数的调用（自适应缩放）===")
n = 0
for mm in re.finditer(r"drawImage\([^)]{40,400}\)", h):
    s = mm.group(0)
    if s.count(",") >= 4:
        print("  @%d: %s" % (mm.start(), s[:200]))
        n += 1
        if n >= 8:
            break
if n == 0:
    print("  没有带目标尺寸的 drawImage（说明按原图尺寸绘制）")
