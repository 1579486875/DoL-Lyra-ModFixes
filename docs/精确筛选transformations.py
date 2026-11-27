# -*- coding: utf-8 -*-
r"""精确筛选：只找路径含 /transformations/ 且被放大的图。

依据（实测）：
  · img/body/**, img/clothes/**, img/sex/*/body/**（不含 transformations）
        -> BESC 整体 2 倍升级，canvas 也是 2 倍，正常
  · img/transformations/**
  · img/sex/*/body/transformations/**
        -> 这一层 canvas 用原尺寸，被放大会只显示左上 1/4（恶魔角错位的根因）
"""
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


o = load(OURS)
b = load(BASE)

todo = []
for n in sorted(set(o) & set(b)):
    if "/transformations/" not in n:
        continue
    so, sb = o[n], b[n]
    if so == sb:
        continue
    if so[0] >= sb[0] and so[1] >= sb[1]:
        todo.append((n.replace("assets/www/", ""), sb, so))

# 原版没有、但在 transformations 下的
extra = []
for n in sorted(set(o) - set(b)):
    if "/transformations/" not in n:
        continue
    extra.append((n.replace("assets/www/", ""), o[n]))

print("=== 需修：原版存在但被放大（%d 张）===" % len(todo))
if todo:
    bydir = defaultdict(list)
    for short, sb, so in todo:
        bydir[short.rsplit("/", 1)[0]].append((short.rsplit("/", 1)[-1], sb, so))
    for d in sorted(bydir):
        print("\n【%s】%d 张" % (d, len(bydir[d])))
        for fn, sb, so in sorted(bydir[d]):
            print("   %-40s %dx%d -> %dx%d" % (fn, sb[0], sb[1], so[0], so[1]))
else:
    print("  无")

print("\n\n=== 原版没有、我们有的（transformations 下，%d 张）===" % len(extra))
if extra:
    bydir2 = defaultdict(list)
    for short, sz in extra:
        bydir2[short.rsplit("/", 1)[0]].append((short.rsplit("/", 1)[-1], sz))
    for d in sorted(bydir2):
        print("\n【%s】%d 张" % (d, len(bydir2[d])))
        for fn, sz in sorted(bydir2[d])[:12]:
            print("   %-40s %dx%d" % (fn, sz[0], sz[1]))
        if len(bydir2[d]) > 12:
            print("   ... 共 %d 张" % len(bydir2[d]))
else:
    print("  无")
