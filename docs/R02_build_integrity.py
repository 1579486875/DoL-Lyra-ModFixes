"""第 2 轮：完整性盘点 —— build_all 的脚本清单与实际文件对账。"""
import os
import re

WORK = r"E:\TAML\_dol\work"
BUILD_ALL = os.path.join(WORK, "build_all.py")

# 关键：必须用 UTF-8 读（PowerShell Get-Content 默认 ANSI 会乱码）
s = open(BUILD_ALL, encoding="utf-8").read()

# 路径是单反斜杠 E:\TAML\_dol\work\xxx.py
PAT = re.compile(r"(?:E:\\TAML\\_dol\\work\\)([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s)

print("=" * 88)
print("build_all.py 脚本清单")
print("=" * 88)
print(f"  共引用 {len(steps)} 个脚本")
print(f"  重复引用: {[x for x in set(steps) if steps.count(x) > 1] or '无'}")

print("\n--- 文件存在性 ---")
missing = []
for f in steps:
    p = os.path.join(WORK, f)
    if not os.path.exists(p):
        missing.append(f)
print(f"  缺失: {missing if missing else '无'}")
for f in missing:
    print(f"    ❌ {f}")

print("\n--- 顺序 ---")
for i, f in enumerate(steps, 1):
    size = ""
    p = os.path.join(WORK, f)
    if os.path.exists(p):
        size = f"{os.path.getsize(p):,}B"
    print(f"  {i:>2}. {f:<36} {size:>9}")

# 关键顺序纪律：TF01 必须最后
print("\n--- 顺序纪律 ---")
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]
print(f"  TF01_nest_guard 位置: {tf}  总步数 {len(steps)}")
if tf and tf[0] != len(steps):
    print(f"  ⚠️ TF01 不是最后一步（后面还有 {len(steps)-tf[0]} 步）")
else:
    print("  ✅ TF01 在最后")

# XC01 必须在 UB01 之后
ub = [i for i, f in enumerate(steps, 1) if f.startswith("UB01")]
xc = [i for i, f in enumerate(steps, 1) if f.startswith("XC01")]
if ub and xc:
    ok = xc[0] > ub[0]
    print(f"  {'✅' if ok else '❌'} XC01({xc[0]}) 在 UB01({ub[0]}) 之后")
else:
    print(f"  UB01: {ub}  XC01: {xc}")

# work 目录里未被 build_all 引用的脚本（可能是死代码/手工脚本）
print("\n--- work 目录脚本 vs build_all ---")
all_py = set(f for f in os.listdir(WORK) if f.endswith(".py"))
referenced = set(steps)
unref = sorted(all_py - referenced)
print(f"  work 里共 {len(all_py)} 个 .py，build_all 引用 {len(referenced)} 个")
print(f"  未被引用 {len(unref)} 个:")
for f in unref[:40]:
    print(f"    {f}")
if len(unref) > 40:
    print(f"    ... 还有 {len(unref)-40} 个")
