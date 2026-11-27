# -*- coding: utf-8 -*-
r"""全量图片尺寸体系审核：按目录找出「偏离该层主流倍数」的文件。

方法：
  1. 对每个 img/ 子目录，统计「原版尺寸 -> 我们尺寸」的映射分布
  2. 取该目录的主流映射（占比最高的）
  3. 找出偏离主流的文件（同目录内尺寸不一致 = 潜在错位）

这比「全局统一 2 倍」更精确：每个目录自己跟自己比，不受目录间差异影响。
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
print("我们的图 %d / 原版 %d / 同名 %d\n" % (len(o), len(b), len(set(o) & set(b))))

# 按目录分组，统计映射
bydir = defaultdict(list)
for n in set(o) & set(b):
    d = n.rsplit("/", 1)[0]
    so, sb = o[n], b[n]
    if so == sb:
        ratio = "same"
    else:
        r = so[0] / sb[0] if sb[0] else 0
        ratio = "x%.2f" % r if abs(r - round(r)) < 0.05 and r > 0 else "irregular"
    bydir[d].append((n.rsplit("/", 1)[-1], sb, so, ratio))

print("=" * 78)
print("各目录的尺寸映射分布（只看有变化的）")
print("=" * 78)
problems = []
for d in sorted(bydir):
    items = bydir[d]
    cnt = Counter(r for _, _, _, r in items)
    if len(cnt) == 1 and "same" in cnt:
        continue
    major, mcount = cnt.most_common(1)[0]
    # 偏离主流的
    odd = [(fn, sb, so, r) for fn, sb, so, r in items if r != major]
    line = "  %-62s 主流 %-9s %d/%d" % (d.replace("assets/www/", ""), major, mcount, len(items))
    if odd:
        line += "  偏离 %d" % len(odd)
        problems.append((d, major, odd))
    print(line)
    if odd:
        for fn, sb, so, r in odd[:4]:
            print("       %-34s %dx%d -> %dx%d  (%s)" % (fn, sb[0], sb[1], so[0], so[1], r))
        if len(odd) > 4:
            print("       ... 共 %d 个" % len(odd))

print("\n" + "=" * 78)
print("=== 汇总：有偏离的目录 %d 个，共 %d 张文件 ===" % (len(problems), sum(len(p[2]) for p in problems)))
print("=" * 78)
for d, major, odd in problems:
    print("  %-62s 主流 %-9s 偏离 %d" % (d.replace("assets/www/", ""), major, len(odd)))
