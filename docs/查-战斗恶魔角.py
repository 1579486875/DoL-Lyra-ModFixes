# -*- coding: utf-8 -*-
"""查战斗小人（dolls）里的恶魔角图，以及它们与身体的对齐情况。"""
import re
import struct
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
names = z.namelist()


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


# 1) dolls 目录里所有含 horn/demon 的图
print("=== dolls/ 里含 horn / demon 的图 ===")
hits = [n for n in names if "/dolls/" in n and re.search(r"horn|demon", n, re.I)]
for n in sorted(hits):
    data = z.read(n)
    print("  %-58s %-12s %6d" % (n.split("/")[-1], png_size(data), len(data)))
print("共", len(hits))

# 2) 全身 doll 图的目录结构
print("\n=== dolls 下的子目录 ===")
dirs = set()
for n in names:
    if "/dolls/" in n and n.endswith(".png"):
        parts = n.split("/dolls/")[1].split("/")
        dirs.add(parts[0] if len(parts) > 1 else "(根)")
for d in sorted(dirs):
    print("  ", d)
