# -*- coding: utf-8 -*-
"""修复 makeFn 兜底查表顺序：NPCNameList_cn_name 必须优先于物种表（Robin 人名 vs 知更鸟）。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

OLD = 'var _keys0 = ["NPCTypeList_cn_name", "NPCTitleList_cn_name"];'
NEW = 'var _keys0 = ["NPCNameList_cn_name", "NPCTitleList_cn_name", "NPCTypeList_cn_name"];'

if OLD not in raw:
    print("❌ 锚点未找到")
    sys.exit(1)

raw2 = raw.replace(OLD, NEW, 1)
print("已把 NPCNameList_cn_name 提到查表顺序首位")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
