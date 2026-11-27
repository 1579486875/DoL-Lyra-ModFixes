# -*- coding: utf-8 -*-
"""找 settings.size 的实际取值，确定 canvas 尺寸。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== 1) size: [...] 形式 ===")
for mm in list(re.finditer(r"size\s*:\s*\[[^\]]{1,40}\]", h))[:30]:
    seg = h[max(0, mm.start() - 250):mm.start() + 100].replace("\n", " ")
    print("  @%d  %s" % (mm.start(), mm.group(0)))
    # 看上下文判断属于哪个组件
    ctx = h[max(0, mm.start() - 400):mm.start()]
    m2 = re.search(r"(name|class|component)\s*:\s*[\"']([^\"']+)", ctx)
    if m2:
        print("        上下文: %s = %s" % (m2.group(1), m2.group(2)))

print("\n\n=== 2) 搜 256, 128 附近的 size 定义 ===")
for mm in list(re.finditer(r"size\s*:\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]", h))[:40]:
    a, b = mm.group(1), mm.group(2)
    if (a, b) in (("256", "128"), ("512", "256"), ("128", "128"), ("512", "128"), ("256", "256")):
        seg = h[max(0, mm.start() - 500):mm.start() + 80]
        m2 = re.search(r"name\s*:\s*[\"']([^\"']+)", seg)
        nm = m2.group(1) if m2 else "?"
        print("  @%d  size:[%s,%s]  name=%s" % (mm.start(), a, b, nm))

print("\n\n=== 3) 关键：characterViewer / body 的尺寸配置 ===")
for kw in ("characterViewer", "sizes:", "MODEL_SIZES", "CANVAS_SIZE"):
    for mm in list(re.finditer(re.escape(kw), h))[:3]:
        print("\n--- %s @%d ---" % (kw, mm.start()))
        print(h[max(0, mm.start() - 300):mm.start() + 600].replace("\n", " ")[:700])
        break
