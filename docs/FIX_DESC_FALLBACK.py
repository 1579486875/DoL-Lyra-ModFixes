# -*- coding: utf-8 -*-
"""给 combatperson 的 description 回落加 setup.description_CN 兜底。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

OLD = "($description_CN || $description)"
NEW = "($description_CN || setup.description_CN($description) || $description)"

cnt = raw.count(OLD)
print("匹配旧写法:", cnt)
if cnt == 0:
    print("⚠ 未找到，检查是否有其他写法")
    for m in list(re.finditer(r"description_CN\s*\|\|", raw))[:10]:
        print("   ", repr(raw[max(0, m.start() - 80):m.start() + 90])[:220])
    sys.exit(0)

raw2 = raw.replace(OLD, NEW)
print("已替换:", cnt, "处")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
