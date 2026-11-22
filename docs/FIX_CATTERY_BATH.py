# -*- coding: utf-8 -*-
"""给猫咖出租屋的 Pc House Bathroom 补大小便入口。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

BLOCK = ('<<bathroomicon "toilet">><<link "小便 (0:01)">><<run Time.pass(60); window.bnSettleNow(); window.bnMoodBoost(100)>><<set $BasicNeeds.bladder to 0>><<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<run window.mee && window.mee.excrete && window.mee.excrete()>><<goto $passage>><</link>><<lstress>>\n'
         '<br>\n'
         '<<bathroomicon "toilet">><<link "大便 (0:05)">><<run Time.pass(300); window.bnSettleNow(); window.bnMoodBoost(100)>><<set $BasicNeeds.digest.anus.volume to 0>><<run window.BN.digestBowels()>><<set $BasicNeeds.bladder to 0>><<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<run window.mee && window.mee.excrete && window.mee.excrete()>><<goto $passage>><</link>><<lstress>>\n'
         '<br><br>\n')

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

found = None
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
        if bj.get("name") == "猫咖出租屋":
            found = (s, zz, bj)
            break
    except Exception:
        continue

if not found:
    print("❌ 没找到猫咖出租屋")
    sys.exit(1)
s_old, zz, bj = found
print("命中:", bj.get("name"), bj.get("version"))

TWEEN = "game/home/home1.twee"
txt = zz.read(TWEEN).decode("utf-8", "replace")
pm = re.search(r"(^:: Pc House Bathroom\s*\n)(.*?)(?=^::|\Z)", txt, re.M | re.S)
if not pm:
    print("⚠ 找不到 Pc House Bathroom")
    sys.exit(1)
body = pm.group(2)
if "小便 (0:01)" in body:
    print("已存在入口")
    sys.exit(0)

ANCHOR = "<<getouticon>><<link [[离开 (0:01)|Pc House]]>><<pass 1>><</link>>"
if ANCHOR not in body:
    print("⚠ 锚点未命中")
    print(repr(body[-600:]))
    sys.exit(1)

new_body = body.replace(ANCHOR, BLOCK + ANCHOR, 1)
txt2 = txt[:pm.start(2)] + new_body + txt[pm.end(2):]

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == TWEEN:
            d = txt2.encode("utf-8")
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
print("✅ 猫咖浴室已加入口")
