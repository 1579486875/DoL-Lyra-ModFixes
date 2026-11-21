# -*- coding: utf-8 -*-
"""CUR22: 修 Forest Shop 的 $gwylanSeen 未初始化红字（②兜底，只改调用点）。

现象：进入 Forest Shop 报
  <<forestShop-main>>: <<elseif>> bad conditional expression:
  TypeError: Cannot read properties of undefined (reading 'includes')
根因：forestShop-main 里 L78/L84 裸调 $gwylanSeen.includes(...)，
      $gwylanSeen 在新档未定义。
修法：只在 forestShop-main widget 内，把 $gwylanSeen.includes( 改成 ($gwylanSeen || []).includes(
      不初始化变量（避免改变 <<if $gwylanSeen>> 的真假语义）。
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
E = lambda s: H.escape(s, quote=False)

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass != 16088:
    print("❌ passage 数异常", npass)
    sys.exit(1)

OPEN = E('<<widget "forestShop-main">>')
CLOSE = E('<</widget>>')
m = re.search(re.escape(OPEN) + r"(.*?)" + re.escape(CLOSE), raw, re.S)
if not m:
    print("❌ 找不到 forestShop-main（raw 形态）")
    sys.exit(1)

body = H.unescape(m.group(1))
orig = body
cnt = body.count("$gwylanSeen.includes(")
body = body.replace("$gwylanSeen.includes(", "($gwylanSeen || []).includes(")
cnt2 = body.count('slot?.type.includes("heavy")')
body = body.replace('slot?.type.includes("heavy")', 'slot?.type?.includes("heavy")')

if body == orig:
    print("✓ 无需修改（可能已修过）")
    sys.exit(0)

new_raw = raw[:m.start(1)] + E(body) + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', new_raw))
if npass2 != npass:
    print("❌ passage 数变化", npass, "->", npass2)
    sys.exit(1)

open(HTML, "wb").write(new_raw.encode("utf-8"))
print("✅ forestShop-main: gwylanSeen 兜底 %d 处, type 可选链 %d 处, passage=%d" % (cnt, cnt2, npass2))
