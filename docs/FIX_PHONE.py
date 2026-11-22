# -*- coding: utf-8 -*-
"""修 SmartPhone：Yenotes 非数组兜底 + SecondPhoneShopGoods 初始化。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")

# 找 SmartPhone 的 base64
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
target = None
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
        if "SmartPhone" in (bj.get("name") or ""):
            target = (s, zz, bj)
            print("命中:", bj.get("name"), bj.get("version"))
            break
    except Exception:
        continue

if not target:
    print("❌ 没找到 SmartPhone")
    sys.exit(1)

s_old, zz, bj = target
js = zz.read("scripts/smartphone-patch.js").decode("utf-8", "replace")

FIXES = [
    ("V.Phone.Yenotes = V.Phone.Yenotes || [];",
     "V.Phone.Yenotes = Array.isArray(V.Phone.Yenotes) ? V.Phone.Yenotes : [];"),
    ("V.Phone.AlarmsToTrigger = V.Phone.AlarmsToTrigger || [];",
     "V.Phone.AlarmsToTrigger = Array.isArray(V.Phone.AlarmsToTrigger) ? V.Phone.AlarmsToTrigger : [];\n    V.Phone.SecondPhoneShopGoods = Array.isArray(V.Phone.SecondPhoneShopGoods) ? V.Phone.SecondPhoneShopGoods : [];"),
    ('V.Phone.Yenotes = V.Phone.Yenotes.filter(y => y.id !== "Landry-AD0")',
     'V.Phone.Yenotes = (Array.isArray(V.Phone.Yenotes) ? V.Phone.Yenotes : []).filter(y => y.id !== "Landry-AD0");'),
]
n = 0
for a, b in FIXES:
    if a not in js:
        print("⚠ 未命中:", a[:60])
        continue
    js = js.replace(a, b, 1)
    n += 1
print("修了", n, "处")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "scripts/smartphone-patch.js":
            d = js.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_zip = buf.getvalue()
new_b64 = base64.b64encode(new_zip).decode("ascii")

raw2 = raw.replace(s_old, new_b64, 1)
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写回 index")
