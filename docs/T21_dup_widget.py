"""T21：扫重复 widget 定义 + widget 参数不匹配。

重复定义会让后一个悄悄覆盖前一个（DoL 有过此问题：
NPCTypeList_cn_name 被赋值两次，后一次 605 字符覆盖前一次 2273 字符）。
"""
import html as H
import re
import sys
from collections import Counter, defaultdict

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("=" * 95)
print("1. 重复的 widget 定义")
print("=" * 95)
defs = defaultdict(list)
for pname, body in PASSAGES.items():
    for m in re.finditer(r'<<widget\s+"([^"]+)"\s*(?:[^>]*)>>', body):
        defs[m.group(1)].append(pname)

dups = {k: v for k, v in defs.items() if len(v) > 1}
print(f"  widget 总数: {len(defs)}")
print(f"  重复定义: {len(dups)}")
for k, v in sorted(dups.items(), key=lambda x: -len(x[1]))[:25]:
    print(f"    {k!r}  ×{len(v)}  in {v[:4]}")

print("\n" + "=" * 95)
print("2. 重复的 <<set setup.xxx>> 赋值（后者覆盖前者）")
print("=" * 95)
sets = defaultdict(list)
for m in re.finditer(r'<<set\s+setup\.(\w+)\s+to\s+"([^"]{0,200})"', g):
    sets[m.group(1)].append((m.start(), len(m.group(2))))

dup_sets = {k: v for k, v in sets.items() if len(v) > 1}
print(f"  重复赋值: {len(dup_sets)}")
for k, v in sorted(dup_sets.items(), key=lambda x: -len(x[1]))[:20]:
    lens = [x[1] for x in v]
    flag = "❌靠后的更短" if lens[-1] < lens[0] else "  "
    print(f"    {flag} setup.{k}  ×{len(v)}  长度 {lens[:6]}")

print("\n" + "=" * 95)
print("3. widget 定义里 <<widget>> 嵌套（应为 0）")
print("=" * 95)
n_nest = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r'<<widget\s+"([^"]+)"[^>]*>>(.*?)<</widget>>', body, re.S):
        if "<<widget" in m.group(2):
            n_nest += 1
            if n_nest <= 8:
                print(f"    {pname}: {m.group(1)!r}")
print(f"  共 {n_nest}")

print("\n" + "=" * 95)
print("4. 重复的 passage 名")
print("=" * 95)
pn = re.findall(r'<tw-passagedata\s+(?![^>]*\\")[^>]*name="([^"]*)"', g)
dupp = {k: v for k, v in Counter(pn).items() if v > 1}
print(f"  {len(dupp)}  {list(dupp.items())[:10]}")
