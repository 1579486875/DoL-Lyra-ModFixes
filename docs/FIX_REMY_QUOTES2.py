# -*- coding: utf-8 -*-
"""块级修复 <<print either(...)>> 内的引号（多行宏）。"""
import re

p = r"E:\TAML\_dol\work\_remy_actions_text_zh.twee"
txt = open(p, encoding="utf-8").read()

def fix_block(m):
    inner = m.group(1)
    inner = inner.replace("“", '"').replace("”", '"')
    inner = inner.replace("‘", "'").replace("’", "'")
    return "<<print either(" + inner + ")>>"

new, n = re.subn(r"<<print either\((.*?)\)>>", fix_block, txt, flags=re.S)
print("修复 either 块:", n)
open(p, "w", encoding="utf-8").write(new)

# 复查：宏内中文引号
bad = []
for m in re.finditer(r"<<(.*?)>>", new, flags=re.S):
    if re.search(r"[“”‘’]", m.group(1)):
        bad.append(m.group(0)[:80])
print("宏内残留:", len(bad))
for b in bad[:3]:
    print("  ", b)
