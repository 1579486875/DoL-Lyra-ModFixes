# -*- coding: utf-8 -*-
"""全量尺寸对照：找出所有「我们包里的同名图与原版尺寸不一致」的情况。

这是「恶魔角浮在头部前方」的通用根因排查：
BESC 美化包把某些 PNG 放大了 2 倍（如 512x128 -> 1024x256），
但游戏 canvas 按原版尺寸绘制，于是放大图只显示左上 1/4 -> 错位。

输出按「放大倍数」分组，便于判断哪些是真错位。
"""
import re
import struct
import zipfile
from collections import defaultdict

OURS = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
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


print("加载中...")
o = load(OURS)
b = load(BASE)
print("我们的图: %d 张" % len(o))
print("原版的图: %d 张" % len(b))

common = set(o) & set(b)
print("同名图: %d 张\n" % len(common))

# 分类
same = []
bigger = []       # 我们更大
smaller = []      # 我们更小
ratio_other = []  # 比例不是整数倍

for n in common:
    so, sb = o[n], b[n]
    if so == sb:
        same.append(n)
        continue
    ro = so[0] / sb[0] if sb[0] else 0
    ry = so[1] / sb[1] if sb[1] else 0
    if abs(ro - ry) < 0.01 and abs(ro - round(ro)) < 0.01 and ro > 1:
        bigger.append((n, sb, so, round(ro, 2)))
    elif abs(ro - ry) < 0.01 and abs(ro - round(ro)) < 0.01 and ro < 1:
        smaller.append((n, sb, so, round(ro, 2)))
    else:
        ratio_other.append((n, sb, so))

print("=" * 72)
print("统计")
print("=" * 72)
print("  尺寸一致    : %d" % len(same))
print("  我们更大    : %d  ← 错位风险" % len(bigger))
print("  我们更小    : %d" % len(smaller))
print("  比例不规则  : %d" % len(ratio_other))

print("\n" + "=" * 72)
print("【我们更大的】按倍数分组（这些是错位嫌疑）")
print("=" * 72)
by_ratio = defaultdict(list)
for n, sb, so, r in bigger:
    by_ratio[r].append((n, sb, so))
for r in sorted(by_ratio, reverse=True):
    items = by_ratio[r]
    print("\n--- %.2f 倍（%d 张）---" % (r, len(items)))
    by_dir = defaultdict(list)
    for n, sb, so in items:
        by_dir[n.rsplit("/", 1)[0]].append((n.rsplit("/", 1)[-1], sb, so))
    for d in sorted(by_dir):
        print("\n  %s  (%d 张)" % (d.replace("assets/www/", ""), len(by_dir[d])))
        for fn, sb, so in sorted(by_dir[d])[:8]:
            print("     %-36s %dx%d -> %dx%d" % (fn, sb[0], sb[1], so[0], so[1]))
        if len(by_dir[d]) > 8:
            print("     ... 共 %d 张" % len(by_dir[d]))

print("\n" + "=" * 72)
print("【我们更小的】（可能是 BESC 降质，一般不影响位置）")
print("=" * 72)
if smaller:
    by_ratio2 = defaultdict(list)
    for n, sb, so, r in smaller:
        by_ratio2[r].append((n, sb, so))
    for r in sorted(by_ratio2):
        print("\n--- %.2f 倍（%d 张）---" % (r, len(by_ratio2[r])))
        for n, sb, so in by_ratio2[r][:10]:
            print("   %-56s %dx%d -> %dx%d" % (n.replace("assets/www/", ""), sb[0], sb[1], so[0], so[1]))
else:
    print("  无")

print("\n" + "=" * 72)
print("【比例不规则】（可能 BESC 重画，一般无害）")
print("=" * 72)
if ratio_other:
    for n, sb, so in ratio_other[:20]:
        print("   %-56s %dx%d -> %dx%d" % (n.replace("assets/www/", ""), sb[0], sb[1], so[0], so[1]))
    if len(ratio_other) > 20:
        print("   ... 共 %d 张" % len(ratio_other))
else:
    print("  无")
