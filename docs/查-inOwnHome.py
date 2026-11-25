# -*- coding: utf-8 -*-
"""查 inOwnHome / inPublic 的实现，看为什么在公园判定为「在家」。"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

for fn in ("inOwnHome", "inPublic"):
    print("=" * 60)
    print("=== %s ===" % fn)
    print("=" * 60)
    for m in re.finditer(r"function\s+" + fn + r"\s*\([^)]*\)\s*\{", s):
        # 提取函数体（平衡括号）
        start = s.index("{", m.start())
        depth = 0
        i = start
        while i < len(s):
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        print(s[m.start():i + 1])
        print()

# 看 onHomeRelief 的调用时机
print("=" * 60)
print("=== onHomeRelief 调用点 ===")
for mm in re.finditer(r"onHomeRelief\s*\(", s):
    print("@%d: %s" % (mm.start(), s[max(0, mm.start() - 400):mm.start() + 200].replace("\n", " ")[:600]))
    print()
