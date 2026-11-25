# -*- coding: utf-8 -*-
"""把 CUR19_pack.py 的 SRC 从早期 backup_r6 改成当前 out 包。"""
import re

P = r"E:\TAML\_dol\work\CUR19_pack.py"
s = open(P, encoding="utf-8").read()

lines = s.split("\n")
for i, l in enumerate(lines):
    if l.strip().startswith("SRC") and "backup_r6" in l:
        print("原:", l)
        lines[i] = 'SRC = r"E:\\TAML\\_dol\\out\\DoL-Lyra-0.5.12.13-CHS-modded.apk"'
        print("新:", lines[i])
        break
else:
    if any(l.strip().startswith("SRC") and "_dol\\out\\DoL-Lyra" in l for l in lines):
        print("SRC 已是 out 包，无需改")
    else:
        print("⚠ 未找到 SRC 行")

open(P, "w", encoding="utf-8").write("\n".join(lines))

print("\n=== 改后 ===")
for l in open(P, encoding="utf-8").read().split("\n"):
    if l.startswith("SRC") or l.startswith("IDX") or l.startswith("DST"):
        print(" ", l)
