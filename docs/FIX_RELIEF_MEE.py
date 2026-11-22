# -*- coding: utf-8 -*-
"""给 BasicNeeds 的 injectRelief 注入代码加 mee.excrete() 联动。"""
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
        if bj.get("name") == "BasicNeeds":
            target = (s, zz, bj)
            break
    except Exception:
        continue
if not target:
    print("❌ 没找到 BasicNeeds")
    sys.exit(1)
s_old, zz, bj = target
print("命中:", bj.get("name"), bj.get("version"))

JS = "scripts/Ban-food.js"
js = zz.read(JS).decode("utf-8", "replace")

OLD = ('<<set $BasicNeeds.bladder to 0>><<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<goto $passage>><</link>><<lstress>>' +
       "' +  '<br><<bathroomicon \"toilet\">><<link \"大便 (0:05)\">><<run Time.pass(300); window.bnSettleNow(); window.bnMoodBoost(100)>><<set $BasicNeeds.digest.anus.volume to 0>><<run window.BN.digestBowels()>><<set $BasicNeeds.bladder to 0>><<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<goto $passage>><</link>><<lstress>>'")

# 更稳的做法：逐个替换两个片段里的 stress 前插入 mee 调用
PEE_OLD = '<<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<goto $passage>>'
PEE_NEW = '<<set $BasicNeeds.bladderFullHrs to 0>><<run window.mee && window.mee.excrete && window.mee.excrete()>><<set $stress to Math.max(0, $stress - 100)>><<goto $passage>>'

c = js.count(PEE_OLD)
print("锚点出现:", c)
if c != 2:
    print("⚠ 预期 2 处，实际 %d，拒绝修改" % c)
    sys.exit(1)
js2 = js.replace(PEE_OLD, PEE_NEW)
print("替换后长度:", len(js), "->", len(js2))

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == JS:
            d = js2.encode("utf-8")
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
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
