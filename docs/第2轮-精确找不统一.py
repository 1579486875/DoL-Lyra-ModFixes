# -*- coding: utf-8 -*-
r"""精确找出「原版该目录尺寸统一，但我们不统一」的情况 —— 这才是我们的问题。

逻辑：
  原版某目录内 N 个文件尺寸全相同 -> 该层 canvas 就是这个尺寸
  我们同目录内尺寸出现 >=2 种 -> 必然有一批显示错位/变小
  -> 统一到「原版尺寸 x 主流倍数」

排除：
  原版本来就不统一的目录（那是游戏设计，如 4 帧动画不同长度）
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

# 按目录分组（只取两边都有的）
bydir_o = defaultdict(dict)
bydir_b = defaultdict(dict)
for n in set(o) & set(b):
    d = n.rsplit("/", 1)[0]
    bydir_o[d][n] = o[n]
    bydir_b[d][n] = b[n]

report = []
for d in sorted(bydir_o):
    ob = bydir_b[d]
    oo = bydir_o[d]
    base_sizes = set(ob.values())
    our_sizes = set(oo.values())
    if len(base_sizes) != 1:
        continue          # 原版本身就不统一，跳过
    if len(our_sizes) <= 1:
        continue          # 我们统一，没问题
    # 原版统一，我们不统一
    cnt = Counter(oo.values())
    major, mcount = cnt.most_common(1)[0]
    base_sz = next(iter(base_sizes))
    odd = [(n, ob[n], oo[n]) for n in oo if oo[n] != major]
    report.append({
        "dir": d,
        "base": base_sz,
        "major": major,
        "major_count": mcount,
        "total": len(oo),
        "odd": odd,
    })

print("=" * 80)
print("原版统一但我们不统一的目录：%d 个" % len(report))
print("=" * 80)

total_odd = 0
for r in report:
    r_ratio = r["major"][0] / r["base"][0] if r["base"][0] else 0
    print("\n【%s】" % r["dir"].replace("assets/www/", ""))
    print("   原版统一 %dx%d  我们主流 %dx%d (x%.2f) %d/%d  偏离 %d" % (
        r["base"][0], r["base"][1], r["major"][0], r["major"][1],
        r_ratio, r["major_count"], r["total"], len(r["odd"])))
    for n, sb, so in sorted(r["odd"])[:8]:
        print("      %-40s 原版 %dx%d  我们 %dx%d" % (
            n.rsplit("/", 1)[-1], sb[0], sb[1], so[0], so[1]))
    if len(r["odd"]) > 8:
        print("      ... 共 %d 个" % len(r["odd"]))
    total_odd += len(r["odd"])

print("\n" + "=" * 80)
print("合计需修：%d 张" % total_odd)
print("=" * 80)
