# -*- coding: utf-8 -*-
"""给 setup.NPC_CN_TOOLNAME 补上 pen / pencil / marker 等书写工具。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

ANCHOR = '"stroker": "飞机杯"'
if ANCHOR not in raw:
    print("❌ 锚点未找到")
    sys.exit(1)

ADD = '"stroker": "飞机杯", "pen": "笔", "pencil": "铅笔", "marker": "马克笔", "brush": "画笔", "crayon": "蜡笔", "quill": "羽毛笔", "chalk": "粉笔"'
raw2 = raw.replace(ANCHOR, ADD, 1)
print("已补工具名映射")

# 顺便看一下 lefttool 可能取哪些值
for kw in ('"pen"', 'lefttool', 'righttool'):
    print("  %-12s count=%d" % (kw, raw2.count(kw)))

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
