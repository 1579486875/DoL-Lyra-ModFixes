# -*- coding: utf-8 -*-
"""给 Fishing Moor Hiker Molestation Finish 补 else 兜底（用转义形式匹配）。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r'(<tw-passagedata[^>]*name="Fishing Moor Hiker Molestation Finish"[^>]*>)(.*?)(</tw-passagedata>)', raw, re.S)
if not m:
    print("❌ 未找到 passage")
    sys.exit(1)

body = m.group(2)
print("原 body 长度:", len(body))

END = "&lt;&lt;/if&gt;&gt;"
idx = body.rfind(END)
if idx < 0:
    print("❌ 未找到转义 </if>")
    print("尾部:", repr(body[-300:]))
    sys.exit(1)

print("最后 </if> @", idx, "其后:", repr(body[idx:])[:200])

GUARD = ('&lt;&lt;else&gt;&gt;\n'
         '\t\t&lt;&lt;clotheson&gt;&gt;\n'
         '\t\t&lt;&lt;endcombat&gt;&gt;\n'
         '\t\t&lt;&lt;clearNPC "moor_hiker_1"&gt;&gt;\n'
         '\t\t&lt;&lt;clearNPC "moor_hiker_2"&gt;&gt;\n'
         '\t\t&lt;&lt;link [[继续|Fishing Moor Wait]]&gt;&gt;&lt;&lt;/link&gt;&gt;\n'
         '\t\t&lt;br&gt;\n'
         '\t\t&lt;&lt;link [[离开|Moor]]&gt;&gt;&lt;&lt;set $eventskip to 1&gt;&gt;&lt;&lt;/link&gt;&gt;\n'
         '\t')

new_body = body[:idx] + GUARD + body[idx:]
raw2 = raw[:m.start(2)] + new_body + raw[m.end(2):]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2, "| 新 body:", len(new_body))
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
