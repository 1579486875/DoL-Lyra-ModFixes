# -*- coding: utf-8 -*-
"""给 setup.NPCTypeList_cn_name 补上 NPC title 映射（NPC_CN_TITLE 共用此表）。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r'(setup\.NPCTypeList_cn_name\s+to\s+")(.*?)(")', raw, re.S)
if not m:
    print("❌ 未找到物种表")
    sys.exit(1)

table = m.group(2)
ADD = {
    "alpha": "头狼",
    "photographer": "摄影师",
    "mayor": "镇长",
    "farmhand": "农场工",
    "terror": "恐怖",
    "smuggler": "走私者",
    "faithful": "忠贞者",
    "reflection": "倒影",
    "captain": "船长",
    "horror": "恐魔",
}

added = []
for k, v in ADD.items():
    if (k + ",") in table:
        continue
    table += "|%s,%s" % (k, v)
    added.append(k)

print("新增:", added if added else "无（已全存在）")
raw2 = raw[:m.start(2)] + table + raw[m.end(2):]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
