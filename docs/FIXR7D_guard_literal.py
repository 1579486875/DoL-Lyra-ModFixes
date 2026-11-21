# -*- coding: utf-8 -*-
"""FIX-R7D：把 guard 里的 <<br>> 字面量改成拼接形式，避免 F.no_<<br>> 误报。"""
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

OLD1 = 'if (p && typeof p.text === "string" && p.text.indexOf("<<br>>") !== -1) {\n        p.text = p.text.replace(/<<br>>/g, "<br>");\n      }'
NEW1 = ('if (p && typeof p.text === "string") {\n'
        '        var BAD = "<<" + "br>>";\n'
        '        if (p.text.indexOf(BAD) !== -1) { p.text = p.text.split(BAD).join("<br>"); }\n'
        '      }')

cnt = 0
for a, b in ((E(OLD1), E(NEW1)), (OLD1, NEW1)):
    if a in raw:
        c = raw.count(a)
        raw = raw.replace(a, b)
        cnt += c

print("替换", cnt, "处")
if cnt == 0:
    print("⚠ 未命中（可能已改）")
else:
    npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
    if npass2 != npass:
        print("❌ passage 变化")
        sys.exit(1)
    open(HTML, "wb").write(raw.encode("utf-8"))
    print("✅ 写入")

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("index 内 <<br>> 剩余:", g.count("<<br>>"))
