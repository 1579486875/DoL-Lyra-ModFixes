"""第 43 轮：修组合 case + C.npc 中文索引 + nnpc_his 参数。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 88)
print("1) 组合 case 现状")
print("=" * 88)
for m in re.finditer(r'<<case\s+("黑狼"|"巨鹰")[^>]*>>', g):
    print(f"  @{m.start()}: {m.group(0)!r}")

print("\n" + "=" * 88)
print("2) C.npc 中文索引")
print("=" * 88)
for m in re.finditer(r'C\.npc\[\s*"(巨鹰|黑狼|象牙幽灵|夜魔)"\s*\]', g):
    print(f"  @{m.start()}: {g[max(0,m.start()-100):m.start()+150]!r}")

print("\n" + "=" * 88)
print("3) nnpc_his / nnpc_her 等 widget 的参数")
print("=" * 88)
for m in re.finditer(r'<<nnpc_\w+\s+"(巨鹰|黑狼)"', g):
    print(f"  @{m.start()}: {g[max(0,m.start()-80):m.start()+120]!r}")

print("\n" + "=" * 88)
print("4) nnpc_his 的 widget 定义（看参数怎么用）")
print("=" * 88)
m = re.search(r'<<widget "nnpc_his">>(.{0,600})<</widget>>', g, re.S)
if m:
    print(m.group(0)[:700])
else:
    # 找定义
    for mm in re.finditer(r'nnpc_his', g):
        print(f"  @{mm.start()}: {g[max(0,mm.start()-100):mm.start()+200]!r}")
        break

print("\n" + "=" * 88)
print("5) 执行修复")
print("=" * 88)

FIXES = [
    # 组合 case
    ('<<case "黑狼" "巨鹰" "Night Monster">>', '<<case "Black Wolf" "Great Hawk" "Night Monster">>'),
    # C.npc 中文索引
    ('C.npc["巨鹰"]', 'C.npc["Great Hawk"]'),
    ('C.npc["黑狼"]', 'C.npc["Black Wolf"]'),
    ('C.npc["象牙幽灵"]', 'C.npc["Ivory Wraith"]'),
    ('C.npc["夜魔"]', 'C.npc["Night Monster"]'),
    # nnpc_* 参数
    ('<<nnpc_his "巨鹰">>', '<<nnpc_his "Great Hawk">>'),
    ('<<nnpc_his "黑狼">>', '<<nnpc_his "Black Wolf">>'),
    ('<<nnpc_her "巨鹰">>', '<<nnpc_her "Great Hawk">>'),
    ('<<nnpc_her "黑狼">>', '<<nnpc_her "Black Wolf">>'),
]

total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old} -> {new}  ({n} 处)")
            break
    else:
        pass

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共修 {total} 处")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验：中文 NPC 名残留 ===")
for pat, desc in [
    (r'<<case\s+"(?:巨鹰|黑狼)"', "case 中文NPC"),
    (r'C\.npc\[\s*"(?:巨鹰|黑狼|象牙幽灵|夜魔)"', "C.npc 中文索引"),
    (r'<<nnpc_\w+\s+"(?:巨鹰|黑狼)"', "nnpc_* 中文参数"),
]:
    n = len(re.findall(pat, g2))
    print(f"  {desc}: {n}  {'✅' if n == 0 else '❌'}")

sys.exit(0)
