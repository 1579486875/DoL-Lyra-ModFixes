"""Z02：扫 UI 控件里的英文。

覆盖：
  1. <<link "文本" "tooltip">> 的第 2 参数
  2. <<cycle>> / <<listbox>> 的选项文本
  3. <<textbox>> 的 placeholder
  4. <<npc>> / <<person>> 的 role 显示（setup.NPC_CN_TITLE 覆盖不到的部分）
"""
import html as H
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))


def is_en_text(s, minw=2):
    s = s.strip()
    if not s or re.search(r"[\u4e00-\u9fff]", s):
        return False
    if s.startswith("<") or re.search(r"[${}()\[\];=<>`]", s):
        return False
    if re.search(r"^(?:setup|C\.npc|\$)", s):
        return False
    return len(re.findall(r"[A-Za-z]{2,}", s)) >= minw


print("=" * 95)
print("1. <<link \"文本\" \"tooltip\">> 第 2 参数")
print("=" * 95)
n1 = 0
for m in re.finditer(r'<<link\s+"[^"]*"\s+"([^"]{4,200})"', g):
    if is_en_text(m.group(1), 2):
        n1 += 1
        if n1 <= 20:
            print(f"  {m.group(1)!r}")
print(f"  共 {n1} 处")

print("\n" + "=" * 95)
print("2. <<cycle>> 选项")
print("=" * 95)
n2 = 0
for m in re.finditer(r"<<cycle\s+[^>]{0,500}?>>", g):
    body = m.group(0)
    # 提取引号里的选项
    opts = re.findall(r'"([^"]{2,60})"', body)
    en = [o for o in opts if is_en_text(o, 1)]
    if en and len(en) == len(opts):
        n2 += 1
        if n2 <= 15:
            print(f"  {en[:4]}")
print(f"  共 {n2} 处（全部选项都是英文的）")

print("\n" + "=" * 95)
print("3. <<listbox>> 选项")
print("=" * 95)
n3 = 0
for m in re.finditer(r"<<listbox\s+[^>]{0,200}?>>(.*?)<</listbox>>", g, re.S):
    body = m.group(0)
    opts = re.findall(r'<<option\s+"([^"]{2,80})"', body)
    en = [o for o in opts if is_en_text(o, 1)]
    if en and len(en) == len(opts) and len(opts) >= 2:
        n3 += 1
        if n3 <= 15:
            print(f"  {en[:4]}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("4. <<textbox>> placeholder（第 3 参数）")
print("=" * 95)
n4 = 0
for m in re.finditer(r'<<textbox\s+"[^"]*"\s+"[^"]*"\s+"([^"]{3,120})"', g):
    if is_en_text(m.group(1), 2):
        n4 += 1
        if n4 <= 15:
            print(f"  {m.group(1)!r}")
print(f"  共 {n4} 处")

print("\n" + "=" * 95)
print("5. <<option>> 选项（独立使用）")
print("=" * 95)
n5 = 0
for m in re.finditer(r'<<option\s+"([^"]{3,120})"', g):
    if is_en_text(m.group(1), 3):
        n5 += 1
        if n5 <= 20:
            print(f"  {m.group(1)!r}")
print(f"  共 {n5} 处")

print("\n" + "=" * 95)
print("6. <<npc>> 的 role 参数（可能是英文 role 名）")
print("=" * 95)
n6 = 0
roles = Counter()
for m in re.finditer(r'<<npc\s+[^>]{0,100}?>>', g):
    pass
for m in re.finditer(r'<<set\s+\$role\s+to\s+"([^"]+)"', g):
    roles[m.group(1)] += 1
print(f"  $role 赋值 {sum(roles.values())} 次，{len(roles)} 种")
for r, c in roles.most_common(20):
    print(f"    {c:>3}  {r!r}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  link tooltip:  {n1}")
print(f"  cycle 全英:    {n2}")
print(f"  listbox 全英:  {n3}")
print(f"  textbox 占位:  {n4}")
print(f"  option 英文:   {n5}")
