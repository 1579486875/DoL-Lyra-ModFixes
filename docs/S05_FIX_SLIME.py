# -*- coding: utf-8 -*-
"""补 giant slime / giant lurker 等缺失物种。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r'(setup\.NPCTypeList_cn_name\s+to\s+")(.*?)(")', raw, re.S)
table = m.group(2)

ADD = {
    "giant slime": "巨型史莱姆",
    "giant lurker": "巨大潜伏者",
    "slime": "史莱姆",
    "lurker": "潜伏者",
}

added = []
for k, v in ADD.items():
    if (k + ",") in table:
        continue
    table += "|%s,%s" % (k, v)
    added.append(k)

print("新增:", added if added else "无")
raw2 = raw[:m.start(2)] + table + raw[m.end(2):]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2, "| 条目:", len(table.split("|")))
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
