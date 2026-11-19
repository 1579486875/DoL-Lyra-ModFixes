"""轮11：判断值 vs 数据源不匹配检测。

方法：
1. 收集所有 <<set $X to "字面值">> 的字面值集合
2. 收集所有 <<if $X is "值">> / <<case "值">> 的判断值
3. 找出「判断值含中文，但同名字面值赋值只有英文」的矛盾
"""
import html
import re
import sys
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

# 1) 所有 <<set $X to "值">> 的字面值（按变量名分组）
set_lit = defaultdict(set)
for m in re.finditer(r'<<set\s+(\$[\w.\[\]]+)\s+to\s+"([^"]*)"', mg):
    set_lit[m.group(1)].add(m.group(2))

print(f"有字面值赋值的变量: {len(set_lit)}")

# 2) 所有 <<if $X is "值">> 的判断
if_check = []
for m in re.finditer(r'<<if\s+(\$[\w.\[\]]+)\s+(is|isnot)\s+"([^"]*)"', mg):
    if_check.append((m.group(1), m.group(2), m.group(3), m.start()))

print(f"<<if>> 字面值判断: {len(if_check)}")

# 3) 找矛盾：判断值含中文但同变量赋值只有英文
mismatch = []
for var, op, val, pos in if_check:
    if not CJK.search(val):
        continue
    lits = set_lit.get(var, set())
    if not lits:
        continue
    has_cn = any(CJK.search(x) for x in lits)
    has_en = any(re.match(r"^[A-Za-z]", x) for x in lits)
    if has_en and not has_cn:
        mismatch.append((var, val, sorted(lits)[:4], pos))

print(f"\n矛盾（判断中文 / 赋值只有英文）: {len(mismatch)}")
for var, val, lits, pos in mismatch[:20]:
    print(f"\n  {var} is {val!r}")
    print(f"    赋值候选: {lits}")
    print(f"    {mg[max(0,pos-120):pos+180]!r}")

# 4) 找 <<case>> 的矛盾（switch 变量 vs case 值）
print("\n" + "=" * 90)
print("<<switch>> 变量 vs <<case>> 值")
print("=" * 90)
switch_blocks = []
for m in re.finditer(r'<<switch\s+(\$[\w.\[\]]+)>>(.*?)<</switch>>', mg, re.S):
    var = m.group(1)
    body = m.group(2)
    cases = re.findall(r'<<case\s+("(?:[^"]*)"(?:\s+"[^"]*")*)>>', body)
    all_vals = []
    for c in cases:
        all_vals.extend(re.findall(r'"([^"]*)"', c))
    switch_blocks.append((var, all_vals, m.start()))

print(f"switch 块: {len(switch_blocks)}")
bad_switch = []
for var, vals, pos in switch_blocks:
    cn_vals = [v for v in vals if CJK.search(v)]
    if not cn_vals:
        continue
    lits = set_lit.get(var, set())
    if not lits:
        continue
    has_en = any(re.match(r"^[A-Za-z]", x) for x in lits)
    has_cn = any(CJK.search(x) for x in lits)
    if has_en and not has_cn:
        bad_switch.append((var, cn_vals[:4], sorted(lits)[:4], pos))

for var, cn_vals, lits, pos in bad_switch[:15]:
    print(f"\n  switch {var}")
    print(f"    case 中文: {cn_vals}")
    print(f"    赋值英文: {lits}")
    print(f"    {mg[max(0,pos-80):pos+200]!r}")

print("\n" + "=" * 90)
print(f"结论：if 矛盾 {len(mismatch)} 项 / switch 矛盾 {len(bad_switch)} 项")
print("=" * 90)

if mismatch or bad_switch:
    sys.exit(1)
print("  ✅ 无矛盾")
sys.exit(0)
