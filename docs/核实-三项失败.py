# -*- coding: utf-8 -*-
"""核实三项「失败」：corset 路径、demon/horns 路径与尺寸分布。"""
import re
import struct
import zipfile
from collections import defaultdict

z = zipfile.ZipFile(r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk")
names = z.namelist()


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


print("=== 1) 所有含 corset 的路径 ===")
cs = [n for n in names if "corset" in n.lower()]
print("共 %d 个" % len(cs))
for n in cs[:30]:
    sz = png_size(z.read(n))
    print("  %-60s %s" % (n.replace("assets/www/", ""), "%dx%d" % sz if sz else ""))

print("\n=== 2) 所有含 demon/horns 的路径（按目录分组）===")
hs = [n for n in names if "demon" in n.lower() and "horn" in n.lower()]
print("共 %d 个" % len(hs))
bydir = defaultdict(list)
for n in hs:
    sz = png_size(z.read(n))
    d = n.rsplit("/", 1)[0].replace("assets/www/", "")
    bydir[d].append((n.rsplit("/", 1)[-1], sz))

for d in sorted(bydir):
    print("\n  【%s】" % d)
    sizes = defaultdict(int)
    for fn, sz in bydir[d]:
        sizes[sz] += 1
    for sz, c in sorted(sizes.items(), key=lambda x: -x[1]):
        print("     %s : %d 个" % ("%dx%d" % sz if sz else "非PNG", c))
    for fn, sz in sorted(bydir[d])[:6]:
        print("       %-40s %s" % (fn, "%dx%d" % sz if sz else ""))
