# -*- coding: utf-8 -*-
"""把 SmartPhone PhotoPack 加进 index。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
PK = r"E:\TAML\_dol\work\photopack.zip"

zp = zipfile.ZipFile(PK)
bj = json.loads(zp.read("boot.json").decode("utf-8-sig"))
NAME = bj.get("name")
print("图包:", NAME, bj.get("version"))

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
body = m.group(1)

# 检查是否已存在
old = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', body):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        z2 = zipfile.ZipFile(io.BytesIO(d))
        b2 = json.loads(z2.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if (b2.get("name") or "") == NAME:
        old = s
        break

new_b64 = base64.b64encode(open(PK, "rb").read()).decode("ascii")

if old:
    body2 = body.replace(old, new_b64, 1)
    print("⚠ 已存在，替换")
else:
    body2 = body.rstrip().rstrip(",") + ',\n"' + new_b64 + '"'
    print("➕ 新增")

raw2 = raw[:m.start(1)] + body2 + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
n_b = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', body))
n_a = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 条目:", n_b, "->", n_a)

if npass2 != npass:
    sys.exit(1)
if not old and n_a != n_b + 1:
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
