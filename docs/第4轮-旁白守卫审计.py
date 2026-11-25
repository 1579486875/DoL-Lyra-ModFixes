# -*- coding: utf-8 -*-
"""第4轮：审计所有 ShowBanner 调用点，确认每个旁白都有明确的触发守卫。"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

def extract_fn(name):
    m = re.search(r"function\s+" + name + r"\s*\([^)]*\)\s*\{", s)
    if not m:
        return None, -1, -1
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
    return s[m.start():i + 1], m.start(), i

# 找所有 ShowBanner('xxx') 的调用
banners = sorted(set(re.findall(r"ShowBanner\('([^']+)'\)", s)))
print("旁白类型: %d 个" % len(banners))
for b in banners:
    print("  ", b)

# 找所有 onXxx 函数，检查每个 ShowBanner 前的守卫
print("\n" + "=" * 70)
print("=== 各函数里的守卫检查 ===")
print("=" * 70)
fns = sorted(set(re.findall(r"function\s+(on\w+)\s*\(", s)))
for fn in fns:
    body, st, en = extract_fn(fn)
    if not body:
        continue
    used = re.findall(r"ShowBanner\('([^']+)'\)", body)
    if not used:
        continue
    # 提取 return 守卫
    guards = []
    for line in body.split("\n"):
        ls = line.strip()
        if ls.startswith("if (") and "return" in ls:
            guards.append(ls[:110])
    print("\n【%s】旁白: %s" % (fn, used))
    if guards:
        for g in guards:
            print("    守卫:", g)
    else:
        print("    ⚠ 无 return 守卫！")
