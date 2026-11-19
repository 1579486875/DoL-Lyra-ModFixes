"""第 26 轮：验证 build_all 顺序，然后触发重建。"""
import os
import re
import subprocess
import sys

WORK = r"E:\TAML\_dol\work"
BA = os.path.join(WORK, "build_all.py")

s = open(BA, encoding="utf-8").read()
PAT = re.compile(r"(?:E:\\TAML\\_dol\\work\\)([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s)

print(f"build_all 共 {len(steps)} 步")
for i, f in enumerate(steps, 1):
    mark = ""
    if f.startswith("ZZ01"):
        mark = "  ← 最终守卫"
    if f.startswith("TF01"):
        mark = "  ← 必须最后"
    if f.startswith("R24"):
        mark = "  ← 新增翻译"
    if mark:
        print(f"  {i:>2}. {f}{mark}")

# 纪律检查
zz = [i for i, f in enumerate(steps, 1) if f.startswith("ZZ01")]
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]
r24 = [i for i, f in enumerate(steps, 1) if f.startswith("R24")]
ub = [i for i, f in enumerate(steps, 1) if f.startswith("UB01")]

print()
ok = True
if not tf:
    print("❌ 缺 TF01")
    ok = False
elif tf[0] != len(steps):
    print(f"❌ TF01 不是最后（在 {tf[0]}/{len(steps)}）")
    ok = False
else:
    print(f"✅ TF01 最后（{tf[0]}）")

if zz and tf and zz[0] < tf[0]:
    print(f"✅ ZZ01({zz[0]}) 在 TF01({tf[0]}) 之前")
else:
    print("❌ ZZ01 位置不对")
    ok = False

if r24 and ub and r24[0] > ub[0]:
    print(f"✅ R24({r24[0]}) 在 UB01({ub[0]}) 之后")
else:
    print(f"⚠️ R24({r24}) / UB01({ub}) 顺序需确认")
    ok = False

if not ok:
    sys.exit(1)

print("\n开始重建 ...")
r = subprocess.run([sys.executable, os.path.join(WORK, "build.py"),
                    "R24 翻译 + 最终守卫 + 三重尖括号修复"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
print(out[-2000:])
sys.exit(r.returncode)
