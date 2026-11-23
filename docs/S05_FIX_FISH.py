# -*- coding: utf-8 -*-
"""补全常见鱼种与水生生物。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r'(setup\.NPCTypeList_cn_name\s+to\s+")(.*?)(")', raw, re.S)
table = m.group(2)

ADD = {
    "carp": "鲤鱼",
    "catfish": "鲶鱼",
    "sardine": "沙丁鱼",
    "ray": "鳐鱼",
    "flatfish": "比目鱼",
    "anchovy": "鳀鱼",
    "clownfish": "小丑鱼",
    "goldfish": "金鱼",
    "koi": "锦鲤",
    "jellyfish": "水母",
    "starfish": "海星",
    "crab": "螃蟹",
    "lobster": "龙虾",
    "shrimp": "虾",
    "clam": "蛤蜊",
    "mussel": "贻贝",
}

added = []
for k, v in ADD.items():
    if (k + ",") in table:
        continue
    table += "|%s,%s" % (k, v)
    added.append(k)

print("新增 %d 项: %s" % (len(added), added))
raw2 = raw[:m.start(2)] + table + raw[m.end(2):]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2, "| 条目:", len(table.split("|")))
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
