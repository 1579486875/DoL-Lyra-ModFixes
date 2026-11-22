# -*- coding: utf-8 -*-
"""插入用户点名的 4 个模组（完整 base64 判重）。"""
import base64
import json
import os
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
DL = r"E:\TAML\_dol\work\_downloads"
FILES = ["GuideToMe.zip", "NoTraumaClamp_0.2.1.zip", "SmartPhone.Alpha-v0.3.91.1.mod.zip", "DOLI.mod.zip"]

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)

added = 0
for fn in FILES:
    p = os.path.join(DL, fn)
    data = open(p, "rb").read()
    z = zipfile.ZipFile(p)
    bj = json.loads(z.read("boot.json").decode("utf-8-sig"))
    nm = bj.get("name", fn)
    b64 = base64.b64encode(data).decode("ascii")
    if b64 in block:
        print("  skip(已存在):", nm)
        continue
    block = block.rstrip()
    if not block.endswith(","):
        block += ","
    block += '\n"' + b64 + '"'
    added += 1
    print("  + %-24s %8d" % (nm, len(data)))

raw2 = raw[:m.start(1)] + block + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2, "| 新增", added)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入，size", len(raw2))
