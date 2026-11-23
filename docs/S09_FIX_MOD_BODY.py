# -*- coding: utf-8 -*-
"""给 Npc Name CN 模组的 BODYPARTS 表补 right/left 及空格形式。"""
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
    if (bj.get("name") or "") == "Npc Name CN":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到 Npc Name CN")
    sys.exit(1)

s_old, zz, bj = target
t = zz.read("npcNameCN.js").decode("utf-8", "replace")

ADD = [
    ('"right": "右"', '"right": "右", "left": "左", "right hand": "右手", "left hand": "左手", "right foot": "右脚", "left foot": "左脚", "right arm": "右臂", "left arm": "左臂"'),
]

# 在 BODYPARTS = { 后插入
mm = re.search(r"(BODYPARTS\s*=\s*\{)", t)
if not mm:
    print("❌ 未找到 BODYPARTS 表")
    sys.exit(1)

anchor = mm.group(1)
newt = t.replace(anchor, anchor + "\n        " + ADD[0][1] + ",", 1)
print("已插入:", ADD[0][1][:120])

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "npcNameCN.js":
            d = newt.encode("utf-8")
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
