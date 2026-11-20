"""N06：查 $description_CN 的赋值与使用。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. $description_CN 赋值")
print("=" * 95)
for m in re.finditer(r"description_CN\s+to\s", g):
    print(f"  @{m.start()}: {g[max(0,m.start()-120):m.start()+180]!r}\n")

print("=" * 95)
print("2. $description 赋值（英文）")
print("=" * 95)
n = 0
for m in re.finditer(r"\$description\s+to\s", g):
    n += 1
    if n <= 15:
        print(f"  @{m.start()}: {g[max(0,m.start()-120):m.start()+150]!r}")
print(f"  共 {n} 处")

print("\n" + "=" * 95)
print("3. person / person1 / persons 等 widget 里用 description 的")
print("=" * 95)
PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

for wname in ("person", "person1", "persons", "personsimple", "combatperson", "beasttype"):
    for pname, body in PASSAGES.items():
        mm = re.search(r'<<widget "' + wname + r'">>(.*?)<</widget>>', body, re.S)
        if not mm:
            continue
        wb = mm.group(1)
        uses = "description_CN" in wb
        print(f"  [<<{wname}>>] 用 description_CN: {uses}")
        if not uses and "description" in wb:
            print(f"    ⚠️ 只用 description: {wb[:300]!r}")
        break
