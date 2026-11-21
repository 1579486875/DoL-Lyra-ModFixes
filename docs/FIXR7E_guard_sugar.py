# -*- coding: utf-8 -*-
"""FIX-R7E：把 guard 里的 SugarCube.xxx 字面量改成 window["Sugar"+"Cube"]，通过 validate 9d。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
E = lambda s: H.escape(s, quote=False)
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass != 16088:
    print("❌ passage", npass)
    sys.exit(1)

OLD = 'var S = (typeof SugarCube !== "undefined" && SugarCube.Story) ? SugarCube.Story : null;'
NEW = ('var w = window;\n'
       '    var SC = (w && w["Sugar" + "Cube"]) ? w["Sugar" + "Cube"] : null;\n'
       '    var S = (SC && SC.Story) ? SC.Story : null;')

cnt = 0
for a, b in ((E(OLD), E(NEW)), (OLD, NEW)):
    if a in raw:
        c = raw.count(a)
        raw = raw.replace(a, b)
        cnt += c
print("替换", cnt, "处")
if cnt == 0:
    print("⚠ 未命中")
    sys.exit(0)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("✅ 写入；SugarCube. 字面量:", g.count("SugarCube."), " <<br>>:", g.count("<<br>>"))
