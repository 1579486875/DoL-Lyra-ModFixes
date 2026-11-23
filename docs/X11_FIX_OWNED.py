# -*- coding: utf-8 -*-
"""修 SmartPhone boot.json 剩余 2 处裸读：$Phone.Owned 与 $Phone.photography。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
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
    if (bj.get("name") or "") == "SmartPhone Alpha":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到")
    sys.exit(1)

s_old, zz, bj = target
boot = zz.read("boot.json").decode("utf-8-sig")

# 1) $Phone.Owned 守卫
OLD1 = '($Phone.Owned and $Phone.Owned.length gt 0)'
NEW1 = '($Phone and $Phone.Owned and $Phone.Owned.length gt 0)'
c1 = boot.count(OLD1)
boot = boot.replace(OLD1, NEW1)
print("Owned 守卫:", c1, "处")

# 2) $Phone.photography 三元
OLD2 = "currentValue : $Phone.photography"
NEW2 = "currentValue : ($Phone ? $Phone.photography : 0)"
c2 = boot.count(OLD2)
boot = boot.replace(OLD2, NEW2)
print("photography 三元:", c2, "处")

json.loads(boot)
print("JSON 合法")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "boot.json":
            d = boot.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
