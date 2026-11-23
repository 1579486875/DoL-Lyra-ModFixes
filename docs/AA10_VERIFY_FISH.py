# -*- coding: utf-8 -*-
"""验证 Fishing Moor Hiker Molestation Finish 的 else 兜底与链接数。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))
m = re.search(r'<tw-passagedata[^>]*name="Fishing Moor Hiker Molestation Finish"[^>]*>(.*?)</tw-passagedata>', g, re.S)
b = m.group(1)
print("body 长度:", len(b))
print("末尾 500 字符:", repr(b[-500:]))
print("\n含 <<else>>:", "<<else>>" in b[-700:])
print("link 数:", len(re.findall(r"<<link ", b)))
print("if/elseif/else 结构:")
for mm in re.finditer(r"<<(/?)if\b|<<elseif\b|<<else\b", b):
    ls = b.rfind("\n", 0, mm.start()) + 1
    le = b.find("\n", mm.start())
    print("  @%-5d %s" % (mm.start(), b[ls:le][:100]))
