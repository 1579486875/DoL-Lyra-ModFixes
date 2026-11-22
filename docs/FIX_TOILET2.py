# -*- coding: utf-8 -*-
"""FIX_TOILET2：给 4 个功能性洗浴点补大小便入口。

加：Temple Cloister Showers（神殿回廊淋浴间）、Strip Club Bathroom、
    Clearing Spring（林中泉水）、Bird Tower Rainwater Pool（鹰塔雨水池）。
不加：Temple Vigil / Temple Confessor（仪式净化）、Temple Jordan / Eden Spring（剧情陪浴）、
      Temple Cloister Shower Take（淋浴过程页）。
"""
import html as H
import re
import shutil
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
E = lambda s: H.escape(s, quote=False)

BLOCK = ('<<bathroomicon "toilet">><<link "小便 (0:01)">><<run Time.pass(60); window.bnSettleNow(); window.bnMoodBoost(100)>><<set $BasicNeeds.bladder to 0>><<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<goto $passage>><</link>><<lstress>>\n'
         '<br>\n'
         '<<bathroomicon "toilet">><<link "大便 (0:05)">><<run Time.pass(300); window.bnSettleNow(); window.bnMoodBoost(100)>><<set $BasicNeeds.digest.anus.volume to 0>><<run window.BN.digestBowels()>><<set $BasicNeeds.bladder to 0>><<set $BasicNeeds.bladderFullHrs to 0>><<set $stress to Math.max(0, $stress - 100)>><<goto $passage>><</link>><<lstress>>\n'
         '<br><br>\n')

TARGETS = [
    ("Temple Cloister Showers", "<<getouticon>><<link [[离开|Temple Cloister]]>><</link>>"),
    ("Strip Club Bathroom", "<<getouticon>><<link [[返回俱乐部 (0:01)|Strip Club]]>><<pass 1>><</link>>"),
    ("Clearing Spring", "<<getouticon>><<link [[出去|Eden Clearing]]>><<endevent>><<clotheson>><</link>>"),
    ("Bird Tower Rainwater Pool", "<<getouticon>><<link [[起身|Bird Tower]]>><</link>>"),
]

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if not __import__("os").path.exists(HTML + ".bak_before_toilet2"):
    shutil.copy2(HTML, HTML + ".bak_before_toilet2")
    print("备份 -> .bak_before_toilet2")

changed = 0
for name, anchor in TARGETS:
    m = re.search(r'(<tw-passagedata[^>]*name="%s"[^>]*>)(.*?)(</tw-passagedata>)' % re.escape(name), raw, re.S)
    if not m:
        print("⚠ 找不到 passage:", name)
        continue
    body = m.group(2)
    if "小便 (0:01)" in H.unescape(body):
        print("  已存在，跳过:", name)
        continue
    a = E(anchor)
    if a not in body:
        print("⚠ 锚点未命中:", name)
        continue
    raw = raw[:m.start(2)] + body.replace(a, E(BLOCK) + a, 1) + raw[m.end(2):]
    changed += 1
    print("✅ 已加:", name)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
print("passage:", npass, "->", npass2, "| 改动", changed)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("写入完成")
