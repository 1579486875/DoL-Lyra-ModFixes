"""R17：generateshoppage 的 slot 兜底（修 Forest Shop 崩溃，幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[R17] index 形态异常")
    sys.exit(1)

MARK = "[R17]"
g = H.unescape(data)
if MARK in g:
    print("[R17] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

OLD_RAW = '<<set $_realSlot to ($clothingShopSlot is "all" ? _item.slot : $clothingShopSlot)>>'
NEW_RAW = (
    '<!-- [R17] slot 兜底：模组服装常漏 slot 字段，按 index 反查 -->'
    '<<set $_realSlot to ($clothingShopSlot is "all" '
    '? (_item.slot || Object.keys(setup.clothes).find(_k => _k !== "all" '
    '&& Array.isArray(setup.clothes[_k]) '
    '&& setup.clothes[_k].some(_x => _x && _x.index === _item.index)) || "upper") '
    ': $clothingShopSlot)>>'
)

# 也兼容 [R16] 已经改过的情况 —— 直接把 R16 标记改成 R17
if "[R16]" in g:
    data = data.replace(H.escape("[R16]", quote=False), H.escape("[R17]", quote=False))
    data = data.replace("[R16]", "[R17]")
    open(HTML, "wb").write(data.encode("utf-8"))
    print("[R17] 已把 R16 标记升级为 R17  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))))
    sys.exit(0)

old_esc = H.escape(OLD_RAW, quote=False)
new_esc = H.escape(NEW_RAW, quote=False)

wt = H.escape('<<widget "generateshoppage">>', quote=False)
wi = data.find(wt)
if wi < 0:
    print("[R17] FAIL 找不到 generateshoppage")
    sys.exit(1)
oi = data.find(old_esc, wi)
if oi < 0:
    print("[R17] FAIL 找不到目标行")
    sys.exit(1)
data = data[:oi] + new_esc + data[oi + len(old_esc):]
open(HTML, "wb").write(data.encode("utf-8"))

g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
ok = MARK in g2
print("[R17] 注入%s  passage=%d" % ("成功" if ok else "失败",
      len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace')))))
sys.exit(0 if ok else 1)
