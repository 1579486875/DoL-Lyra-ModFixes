"""第 31 轮：修验证正则（允许 \\ 或 \），确认顺序后重建。"""
import os
import re
import subprocess
import sys

WORK = r"E:\TAML\_dol\work"
BA = os.path.join(WORK, "build_all.py")

s = open(BA, encoding="utf-8").read()
# 允许 1 或 2 个反斜杠
PAT = re.compile(r"E:\\\\?TAML\\\\?_dol\\\\?work\\\\?([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s)

print(f"build_all 共 {len(steps)} 步")
for i, f in enumerate(steps, 1):
    if f.startswith(("R24", "ZZ01", "TF01", "UB01", "ADI01", "ACE01")):
        print(f"  {i:>2}. {f}")

r24 = [i for i, f in enumerate(steps, 1) if f.startswith("R24")]
zz = [i for i, f in enumerate(steps, 1) if f.startswith("ZZ01")]
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]
ub = [i for i, f in enumerate(steps, 1) if f.startswith("UB01")]

print()
ok = True
checks = [
    ("R24 存在", bool(r24)),
    ("TF01 最后", bool(tf) and tf[0] == len(steps)),
    ("ZZ01 在 TF01 前", bool(zz) and bool(tf) and zz[0] < tf[0]),
    ("R24 在 UB01 后", bool(r24) and bool(ub) and r24[0] > ub[0]),
    ("R24 在 ZZ01 前", bool(r24) and bool(zz) and r24[0] < zz[0]),
]
for name, v in checks:
    print(f"  {'✅' if v else '❌'} {name}")
    if not v:
        ok = False

if not ok:
    print("\n顺序不达标，不重建")
    sys.exit(1)

print("\n开始重建 ...")
r = subprocess.run([sys.executable, os.path.join(WORK, "build.py"),
                    "R24 翻译19条 + 最终守卫 + 三重尖括号"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(((r.stdout or "") + (r.stderr or ""))[-2500:])
sys.exit(r.returncode)
