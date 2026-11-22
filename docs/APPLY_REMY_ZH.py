# -*- coding: utf-8 -*-
"""把 795 条译文写回 Remy Love 的 actions-text.twee（保留缩进与宏）。"""
import json
import os
import re
import zipfile

WORK = r"E:\TAML\_dol\work"
SRC = r"E:\TAML\_dol\mods4\Remy.Love.Mod.mod.zip"
OUT = os.path.join(WORK, "_remy_actions_text_zh.twee")

# 合并所有译文
ZH = {}
for i in range(8):
    p = os.path.join(WORK, "_remy_zh_%02d.json" % i)
    if os.path.exists(p):
        ZH.update(json.load(open(p, encoding="utf-8")))
print("译文条目:", len(ZH))

z = zipfile.ZipFile(SRC)
txt = z.read("game/base-combat/actions-text.twee").decode("utf-8", "replace")
lines = txt.split("\n")

out = []
replaced = 0
missed = []
for line in lines:
    stripped = line.strip()
    if stripped in ZH:
        # 保留行首缩进
        indent = line[:len(line) - len(line.lstrip())]
        out.append(indent + ZH[stripped])
        replaced += 1
    else:
        out.append(line)
        # 记录该替换但没匹配的英文行
        if (stripped and not stripped.startswith(("::", "<<", "/*", "//", "<!--"))
                and re.search(r"[A-Za-z]{3,}", stripped)
                and not re.search(r"[\u4e00-\u9fff]", stripped)):
            missed.append(stripped)

new = "\n".join(out)
open(OUT, "w", encoding="utf-8").write(new)
print("替换行数:", replaced, "| 未匹配英文行:", len(missed))
for s in missed[:5]:
    print("  未匹配:", s[:100])
