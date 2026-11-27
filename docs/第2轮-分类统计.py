# -*- coding: utf-8 -*-
r"""把「原版统一但我们不统一」的 404 个目录分成两类，统计规模。

A 类【错位，优先修】：该目录主流 = 原版尺寸（x1.00），少数被放大到 x2
    -> BESC 没升级这层 canvas，放大的图只显示左上 1/4，位置完全错
B 类【变小，次优先】：该目录主流 = x2，少数仍是原版尺寸
    -> canvas 是 x2，没升级的图只占左上角，位置对但变小
C 类【其他倍数】：主流不是 1 或 2，或原版尺寸不规则
"""
import struct
import sys
import zipfile
from collections import Counter, defaultdict

OURS = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def load(apk):
    z = zipfile.ZipFile(apk)
    d = {}
    for n in z.namelist():
        if n.startswith("assets/www/img/") and n.endswith(".png"):
            sz = png_size(z.read(n))
            if sz:
                d[n] = sz
    return d


o = load(OURS)
b = load(BASE)

bydir_o = defaultdict(dict)
bydir_b = defaultdict(dict)
for n in set(o) & set(b):
    d = n.rsplit("/", 1)[0]
    bydir_o[d][n] = o[n]
    bydir_b[d][n] = b[n]

A, B, C = [], [], []
for d in sorted(bydir_o):
    ob, oo = bydir_b[d], bydir_o[d]
    if len(set(ob.values())) != 1:
        continue
    if len(set(oo.values())) <= 1:
        continue
    base_sz = next(iter(set(ob.values())))
    cnt = Counter(oo.values())
    major, mcount = cnt.most_common(1)[0]
    odd = [(n, ob[n], oo[n]) for n in oo if oo[n] != major]
    ratio = major[0] / base_sz[0] if base_sz[0] else 0
    rec = (d, base_sz, major, ratio, odd)
    if abs(ratio - 1.0) < 0.05:
        A.append(rec)          # 主流=原尺寸，少数放大 -> 错位
    elif abs(ratio - 2.0) < 0.05:
        B.append(rec)          # 主流=x2，少数没升级 -> 变小
    else:
        C.append(rec)

print("=" * 76)
print("A 类【错位·优先修】：%d 个目录，%d 张" % (len(A), sum(len(x[4]) for x in A)))
print("B 类【变小·次优先】：%d 个目录，%d 张" % (len(B), sum(len(x[4]) for x in B)))
print("C 类【其他】：      %d 个目录，%d 张" % (len(C), sum(len(x[4]) for x in C)))
print("=" * 76)

print("\n=== A 类明细（错位，图比 canvas 大）===")
for d, base_sz, major, ratio, odd in A:
    print("\n【%s】原版 %dx%d  主流 %dx%d  偏离 %d" % (
        d.replace("assets/www/", ""), base_sz[0], base_sz[1], major[0], major[1], len(odd)))
    for n, sb, so in sorted(odd)[:6]:
        print("    %-38s %dx%d -> %dx%d" % (n.rsplit("/", 1)[-1], sb[0], sb[1], so[0], so[1]))
    if len(odd) > 6:
        print("    ... 共 %d" % len(odd))

print("\n\n=== C 类明细（其他倍数，需人工判断）===")
for d, base_sz, major, ratio, odd in C[:15]:
    print("\n【%s】原版 %dx%d  主流 %dx%d (x%.2f)  偏离 %d" % (
        d.replace("assets/www/", ""), base_sz[0], base_sz[1],
        major[0], major[1], ratio, len(odd)))
    for n, sb, so in sorted(odd)[:5]:
        print("    %-38s %dx%d -> %dx%d" % (n.rsplit("/", 1)[-1], sb[0], sb[1], so[0], so[1]))
