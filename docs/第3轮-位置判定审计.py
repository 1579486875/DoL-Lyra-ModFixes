# -*- coding: utf-8 -*-
"""第3轮：审计所有「位置判定」函数，找同类误判（状态变量当位置用）。"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

def extract_fn(name):
    m = re.search(r"function\s+" + name + r"\s*\([^)]*\)\s*\{", s)
    if not m:
        return None
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
    return s[m.start():i + 1]

FNS = ["inOwnHome", "inPublic", "currentPassage", "ashamedOfNude", "isPregnant"]
for fn in FNS:
    body = extract_fn(fn)
    if not body:
        print("\n=== %s: 未找到 ===" % fn)
        continue
    print("\n" + "=" * 60)
    print("=== %s ===" % fn)
    print("=" * 60)
    print(body)

# 找所有 realEstate / location / passage 的用法
print("\n\n" + "=" * 60)
print("=== 关键状态变量的所有用法 ===")
print("=" * 60)
for kw in ("realEstate", "V.location", "currentPassage()"):
    print("\n--- %s ---" % kw)
    for mm in re.finditer(re.escape(kw), s):
        seg = s[max(0, mm.start() - 120):mm.start() + 150].replace("\n", " ")
        print("  @%-6d %s" % (mm.start(), seg[:250]))
