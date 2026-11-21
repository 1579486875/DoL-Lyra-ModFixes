# -*- coding: utf-8 -*-
"""FIX-R7C：把玩家可见的 "Export" 按钮文本改成"导出"（只改 UI 文本）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass != 16088:
    print("❌ passage 数异常", npass)
    sys.exit(1)

E = lambda s: H.escape(s, quote=False)
total = 0
pairs = [
    ('.text("Export")', '.text("导出")'),
    ('element.text = "Export"', 'element.text = "导出"'),
    ('value="Export"', 'value="导出"'),
    ('label: "Export"', 'label: "导出"'),
]
for old, new in pairs:
    for a, b in ((E(old), E(new)), (old, new)):
        c = raw.count(a)
        if c:
            raw = raw.replace(a, b)
            total += c
            print("  %-30s -> %s  x%d" % (old, new, c))

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass2 != npass:
    print("❌ passage 数变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("✅ 共替换 %d 处，passage=%d" % (total, npass2))
