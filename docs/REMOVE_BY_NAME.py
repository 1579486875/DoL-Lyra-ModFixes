# -*- coding: utf-8 -*-
"""按 boot.json 的 name 移除模组（处理 base64 已被改过的情况）。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
TARGET = "NoTraumaClamp"

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

target_b64 = None
for s in parts:
    try:
        data = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if data[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(data))
        if "boot.json" not in zz.namelist():
            continue
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        if bj.get("name") == TARGET:
            target_b64 = s
            print("找到:", bj.get("name"), bj.get("version"))
            break
    except Exception:
        continue

if not target_b64:
    print("⚠ 没找到", TARGET)
    sys.exit(0)

pat = re.compile(r',?\s*"' + re.escape(target_b64) + r'"')
new_block, cnt = pat.subn("", block, count=1)
print("移除项:", cnt)
raw2 = raw[:m.start(1)] + new_block + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
