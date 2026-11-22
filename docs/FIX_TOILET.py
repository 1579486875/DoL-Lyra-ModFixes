# -*- coding: utf-8 -*-
"""FIX_TOILET：给孤儿院 Bathroom / Bath、妓院 Brothel Bathroom 补 BasicNeeds 大小便入口。

代码沿用 Toilet Addon v1.4（已在 Inn Bathroom / Inn Bath / Flats Own Shower /
Deadwood Property Bathroom 上验证可用）。
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
    # (passage, 锚点(unescaped), 插入位置 after)
    ("Bathroom", "<<personalUpkeep>>", "after"),
    ("Bath", "<<getouticon>><<link [[出去|Bath Finish]]>><</link>>", "before"),
    ("Brothel Bathroom", "<<getouticon>><<link [[妓院 (0:01)|Brothel]]>><<pass 1>><</link>>", "before"),
]

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if not __import__("os").path.exists(HTML + ".bak_before_toilet"):
    shutil.copy2(HTML, HTML + ".bak_before_toilet")
    print("备份 -> .bak_before_toilet")

changed = 0
for name, anchor, where in TARGETS:
    m = re.search(r'(<tw-passagedata[^>]*name="%s"[^>]*>)(.*?)(</tw-passagedata>)' % re.escape(name), raw, re.S)
    if not m:
        print("⚠ 找不到 passage:", name)
        continue
    body = m.group(2)
    a = E(anchor)
    if E("<<bathroomicon \"toilet\">>") in body or "小便 (0:01)" in H.unescape(body):
        print("  已存在，跳过:", name)
        continue
    if a not in body:
        print("⚠ 锚点未命中:", name, anchor[:40])
        continue
    if where == "after":
        new_body = body.replace(a, a + "\n" + E(BLOCK), 1)
    else:
        new_body = body.replace(a, E(BLOCK) + a, 1)
    if new_body == body:
        print("⚠ 未改动:", name)
        continue
    raw = raw[:m.start(2)] + new_body + raw[m.end(2):]
    changed += 1
    print("✅ 已加:", name)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
print("passage:", npass, "->", npass2, "| 改动", changed)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("写入完成")
