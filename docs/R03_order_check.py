"""第 3 轮：顺序纪律验证 —— UB01 会不会重新引入已修的 bug。

检查 UB01_full_bake 的替换来源，以及 printNobody 是从哪个脚本引入的。
"""
import os
import re

WORK = r"E:\TAML\_dol\work"


def read(f):
    return open(os.path.join(WORK, f), encoding="utf-8").read()


print("=" * 88)
print("UB01_full_bake.py 的实现")
print("=" * 88)
ub = read("UB01_full_bake.py")
print(ub[:2500])

print("\n" + "=" * 88)
print("哪个脚本引入了 printNobody")
print("=" * 88)
for f in sorted(os.listdir(WORK)):
    if not f.endswith(".py"):
        continue
    s = read(f)
    if "printNobody" in s:
        print(f"  🎯 {f}")

print("\n" + "=" * 88)
print("哪个脚本引入了 flesh_text / flight_text")
print("=" * 88)
for f in sorted(os.listdir(WORK)):
    if not f.endswith(".py"):
        continue
    s = read(f)
    hits = []
    if "flesh_text" in s:
        hits.append("flesh_text")
    if "flight_text" in s:
        hits.append("flight_text")
    if hits:
        print(f"  {f}: {hits}")
