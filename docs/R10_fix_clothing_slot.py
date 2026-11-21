"""R10：补全 mod 服装缺失的 slot（修 Forest Shop 崩溃，幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[R10] index 形态异常")
    sys.exit(1)

MARK = "[R10]"
g = H.unescape(data)
if MARK in g:
    print("[R10] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

WIDGET_ESC = H.escape('<<widget "clothingShopv2">>', quote=False)
ANCHOR_ESC = H.escape('<<exitclothingshop>>\n', quote=False)

wi = data.find(WIDGET_ESC)
if wi < 0:
    print("[R10] FAIL 找不到 clothingShopv2")
    sys.exit(1)
ai = data.find(ANCHOR_ESC, wi)
if ai < 0:
    print("[R10] FAIL 找不到 exitclothingshop")
    sys.exit(1)

INJECT = (
    '\t<!-- [R10] 补全 mod 服装缺失的 slot（注意：宏表达式里不能用 _变量 当 const/箭头参数名，'
    '引擎会把它改写成 State.temporary.x 导致语法错误 —— 第12轮修正） -->\n'
    '\t<<run (() => {\n'
    '\t\ttry {\n'
    '\t\t\tif (!setup.clothes) return;\n'
    '\t\t\tfor (const sk of Object.keys(setup.clothes)) {\n'
    '\t\t\t\tif (sk === "all" || !Array.isArray(setup.clothes[sk])) continue;\n'
    '\t\t\t\tfor (const sc of setup.clothes[sk]) {\n'
    '\t\t\t\t\tif (sc && !sc.slot) sc.slot = sk;\n'
    '\t\t\t\t}\n'
    '\t\t\t}\n'
    '\t\t} catch (e) { /* ignore */ }\n'
    '\t})()>>\n'
)
ins = H.escape(INJECT, quote=False)
data = data[:ai + len(ANCHOR_ESC)] + ins + data[ai + len(ANCHOR_ESC):]
open(HTML, "wb").write(data.encode("utf-8"))

g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
ok = MARK in g2
print("[R10] 注入%s  passage=%d" % ("成功" if ok else "失败",
      len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace')))))
sys.exit(0 if ok else 1)
