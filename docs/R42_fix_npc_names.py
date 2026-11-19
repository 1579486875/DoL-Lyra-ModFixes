"""第 42 轮：修 NPC 名被翻译导致 <<case>> 永不命中。

setup.NPCNameList = ["...","Black Wolf",...,"Great Hawk","Ivory Wraith",...]
所以 <<case "巨鹰">> / <<case "黑狼">> 永远不匹配 -> 必须改回英文。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 88)
print("1) 确认 NPCNameList 内容")
print("=" * 88)
m = re.search(r"setup\.NPCNameList\s*=\s*\[([^\]]{0,1200})\]", g)
if m:
    items = re.findall(r'"([^"]+)"', m.group(1))
    print(f"  {len(items)} 个: {items}")
    eng = [x for x in items if re.match(r"^[A-Za-z ]+$", x)]
    cn = [x for x in items if re.search(r"[\u4e00-\u9fff]", x)]
    print(f"  英文 {len(eng)} / 中文 {len(cn)}")

print("\n" + "=" * 88)
print("2) 找所有 case 中文NPC名")
print("=" * 88)
NPC_CN = ["巨鹰", "黑狼", "象牙幽灵", "夜魔"]
for n in NPC_CN:
    hits = [(m.start(), m.group(0)) for m in re.finditer(r'<<case\s+"' + re.escape(n) + r'"', g)]
    print(f"  <<case \"{n}\">>: {len(hits)} 处")
    for pos, txt in hits[:3]:
        print(f"    @{pos}: {g[max(0,pos-100):pos+120]!r}")

print("\n" + "=" * 88)
print("3) 找 if is 中文NPC名")
print("=" * 88)
for n in NPC_CN:
    hits = [(m.start(), m.group(0)) for m in re.finditer(r'is\s+"' + re.escape(n) + r'"', g)]
    print(f"  is \"{n}\": {len(hits)} 处")
    for pos, txt in hits[:2]:
        print(f"    @{pos}: {g[max(0,pos-120):pos+120]!r}")

print("\n" + "=" * 88)
print("4) 修 $worn.genitals.name")
print("=" * 88)
# 查物品定义
for m in re.finditer(r'slot:\s*"genitals",\s*\n\s*name:\s*"([^"]+)"', g):
    print(f"  genitals 物品 name: {m.group(1)!r}")
for m in re.finditer(r'name:\s*"(chastity parasite|slimechastitycage)"', g):
    print(f"  找到: {m.group(1)!r}")

print("\n" + "=" * 88)
print("5) 执行修复")
print("=" * 88)

FIXES = [
    ('<<case "巨鹰">>', '<<case "Great Hawk">>'),
    ('<<case "黑狼">>', '<<case "Black Wolf">>'),
    ('<<case "Night Monster">>', '<<case "Night Monster">>'),  # 本来就是英文
    ('is "贞操锁寄生虫"', 'is "chastity parasite"'),
]

total = 0
for old, new in FIXES:
    if old == new:
        continue
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old} -> {new}  ({n} 处)")
            break
    else:
        print(f"  （未命中）{old}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共修 {total} 处，已写回")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
for n in NPC_CN:
    a = len(re.findall(r'<<case\s+"' + re.escape(n) + r'"', g2))
    b = len(re.findall(r'is\s+"' + re.escape(n) + r'"', g2))
    print(f"  {n}: case {a} / is {b}")
print(f"  is \"贞操锁寄生虫\": {len(re.findall(chr(34) + '贞操锁寄生虫' + chr(34), g2))}")

sys.exit(0 if total else 1)
