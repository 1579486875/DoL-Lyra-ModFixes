# -*- coding: utf-8 -*-
"""给 Cattery 的 Pc House Bathroom 与 FertilityExpansion 的 Eden Safehouse Bathroom 补大小便入口。"""
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

TARGETS = [
    ("Cattery", "game/home/home1.twee", ":: Pc House Bathroom",
     "<<getouticon>><<link [[离开 (0:01)|Pc House]]>><<pass 1>><</link>>"),
    ("Fertility", "game/eden-safehouse.twee", ":: Eden Safehouse Bathroom",
     "<<personalUpkeep>>"),
]

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

for name_key, twee_name, passage_head, anchor in TARGETS:
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
            if name_key.lower() in (bj.get("name") or "").lower():
                if twee_name in zz.namelist():
                    found = (s, zz, bj)
                    break
        except Exception:
            continue

    print("\n=== %s ===" % name_key)
    if not found:
        print("  未找到模组或 twee")
        continue
    s_old, zz, bj = found
    print("  命中:", bj.get("name"), bj.get("version"))

    txt = zz.read(twee_name).decode("utf-8", "replace")
    # 定位 passage 块
    pm = re.search(r"(^%s[^\n]*\n)(.*?)(?=^::|\Z)" % re.escape(passage_head), txt, re.M | re.S)
    if not pm:
        print("  ⚠ 找不到 passage", passage_head)
        continue
    body = pm.group(2)
    if "小便 (0:01)" in body:
        print("  已存在入口，跳过")
        continue
    if anchor not in body:
        print("  ⚠ 锚点未命中:", anchor)
        continue
    new_body = body.replace(anchor, BLOCK + anchor, 1)
    txt2 = txt[:pm.start(2)] + new_body + txt[pm.end(2):]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zz.infolist():
            d = zz.read(info.filename)
            if info.filename == twee_name:
                d = txt2.encode("utf-8")
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, d)
    new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    raw = raw.replace(s_old, new_b64, 1)
    print("  ✅ 已加入口")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("\npassage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("✅ 写入")
