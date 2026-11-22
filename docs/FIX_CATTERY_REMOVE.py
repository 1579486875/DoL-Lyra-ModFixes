# -*- coding: utf-8 -*-
"""移除猫咖的 Containers 补丁（findString 在静态/运行时间不一致，必然失配）。"""
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
    if bj.get("name") == "猫咖出租屋":
        target = (s, zz, bj)
        break
if not target:
    print("❌ 没找到猫咖")
    sys.exit(1)
s_old, zz, bj = target
print("命中:", bj.get("name"), bj.get("version"))

removed = 0
for a in bj.get("addonPlugin") or []:
    if a.get("addonName") != "TweeReplacerAddon":
        continue
    ps = a.get("params")
    if not isinstance(ps, list):
        continue
    newps = [pt for pt in ps if not (isinstance(pt, dict) and pt.get("passage") == "Containers")]
    removed += len(ps) - len(newps)
    a["params"] = newps
print("移除 Containers 补丁:", removed)
if removed == 0:
    print("未找到该补丁，跳过")
    sys.exit(0)

nb = json.dumps(bj, ensure_ascii=False, indent=2)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "boot.json":
            d = nb.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
