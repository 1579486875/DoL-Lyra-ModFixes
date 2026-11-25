# -*- coding: utf-8 -*-
"""全局找 horn / demon 相关的图。"""
import re
import struct
import zipfile
from collections import defaultdict

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
names = z.namelist()


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


print("=== 所有含 horn 的图 ===")
hits = [n for n in names if n.endswith(".png") and re.search(r"horn", n, re.I)]
for n in sorted(hits):
    d = z.read(n)
    print("  %-70s %-12s %6d" % (n.replace("assets/www/img/", ""), png_size(d), len(d)))
print("共", len(hits))

print("\n=== 所有含 demon 的图（前 30）===")
hits2 = [n for n in names if n.endswith(".png") and re.search(r"demon", n, re.I)]
for n in sorted(hits2)[:30]:
    d = z.read(n)
    print("  %-70s %-12s %6d" % (n.replace("assets/www/img/", ""), png_size(d), len(d)))
print("共", len(hits2))

print("\n=== transformations 目录结构 ===")
dirs = defaultdict(int)
for n in names:
    if "/transformations/" in n and n.endswith(".png"):
        rel = n.split("/transformations/")[1]
        parts = rel.split("/")
        dirs[parts[0] if len(parts) > 1 else "(根)"] += 1
for d, c in sorted(dirs.items()):
    print("  %-24s %d 个" % (d, c))
