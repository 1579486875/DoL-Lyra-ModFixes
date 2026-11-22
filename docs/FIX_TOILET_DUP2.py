# -*- coding: utf-8 -*-
"""用正则删掉 Bathroom 里手工加的解手入口（BasicNeeds 的 RELIEF_SCENES 已自动注入）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
E = lambda s: H.escape(s, quote=False)
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r'(<tw-passagedata[^>]*name="Bathroom"[^>]*>)(.*?)(</tw-passagedata>)', raw, re.S)
if not m:
    print("❌ 找不到 Bathroom")
    sys.exit(1)
body = m.group(2)
print("原 body 长度:", len(body), "| 小便数:", body.count(E("小便 (0:01)")))

# 匹配「小便/大便」整段：从 bathroomicon 到 lstress>>，允许中间任意内容
PEER = re.compile(re.escape(E('<<bathroomicon "toilet">><<link "小便 (0:01)">>')) + r".*?" + re.escape(E("<</link>><<lstress>>")), re.S)
POOR = re.compile(re.escape(E('<<bathroomicon "toilet">><<link "大便 (0:05)">>')) + r".*?" + re.escape(E("<</link>><<lstress>>")), re.S)

new_body, c1 = PEER.subn("", body, count=1)
new_body, c2 = POOR.subn("", new_body, count=1)
print("删除：pee=%d poo=%d" % (c1, c2))
if c1 != 1 or c2 != 1:
    print("⚠ 数量异常，拒绝修改")
    sys.exit(1)

# 清理残留的空行/重复 br
new_body = re.sub(r"(?:[ \t]*<br>\s*){3,}", "<br><br>\n", new_body)
print("新 body 长度:", len(new_body), "| 小便数:", new_body.count(E("小便 (0:01)")))

raw2 = raw[:m.start(2)] + new_body + raw[m.end(2):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
