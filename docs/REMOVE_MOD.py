# -*- coding: utf-8 -*-
"""按完整 base64 从 modDataValueZipList 移除一个模组（默认移除默示录 modpack）。"""
import base64
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
TARGET = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\work\_downloads\revelation-the-book-of-return-v1.4.6.modpack"

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
b64 = base64.b64encode(open(TARGET, "rb").read()).decode("ascii")

if b64 not in block:
    print("✓ 未找到该模组（可能已移除）")
    sys.exit(0)

# 移除包含该 base64 的整个字符串项（含前导逗号/换行）
pat = re.compile(r',?\s*"' + re.escape(b64) + r'"')
new_block, cnt = pat.subn("", block, count=1)
print("移除项:", cnt)
raw2 = raw[:m.start(1)] + new_block + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入，size", len(raw2))
