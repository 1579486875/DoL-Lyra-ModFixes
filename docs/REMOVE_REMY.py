# -*- coding: utf-8 -*-
"""移除 Remy Love（与中文版不兼容，38 个补丁全失配）。"""
import base64
import io
import json
import os
import re
import sys
import zipfile

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
target = None
for s in parts:
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if "Remy" in (bj.get("name") or ""):
        target = (s, bj)
        break
if not target:
    print("未找到 Remy Love（可能已移除）")
    sys.exit(0)
s_old, bj = target
print("移除:", bj.get("name"), bj.get("version"))

pat = re.compile(r',?\s*"' + re.escape(s_old) + r'"')
raw2, cnt = pat.subn("", raw, count=1)
print("移除条目:", cnt)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
