# -*- coding: utf-8 -*-
"""补 _DESC 的 thick 等剩余描述词。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"(var _DESC\s*=\s*\{)(.*?)(\n\s*\};)", raw, re.S)
if not m:
    print("❌ 未找到 _DESC")
    sys.exit(1)

body = m.group(2)
ADD = {
    "thick": "丰腴",
    "stocky": "敦实",
    "sturdy": "结实",
    "willowy": "婀娜",
    "wiry": "精瘦结实",
    "lithe": "轻盈",
    "lanky": "瘦长",
    "voluptuous": "丰满性感",
}
added = []
for k, v in ADD.items():
    if ('"%s"' % k) in body:
        continue
    body = body.rstrip().rstrip(",") + ',\n        "%s": "%s"' % (k, v)
    added.append(k)
print("新增:", added)

raw2 = raw[:m.start(2)] + body + raw[m.end(2):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
