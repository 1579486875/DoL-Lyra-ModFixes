# -*- coding: utf-8 -*-
"""精确列出需要修的「原版存在但被放大 2 倍」的图，限定在 sex/*/body/transformations 与 transformations。

判据（来自实测）：
  · img/body/**, img/clothes/**  -> BESC 整体 2 倍升级，正常，不修
  · img/transformations/**       -> canvas 是原尺寸，被放大会错位，需修（已修）
  · img/sex/*\/body/transformations/** -> 同上，需修
  · img/sex/*\/active/**         -> 原版没有此目录，BESC 新增，暂不动
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

TARGET_PATTERNS = [
    "/img/transformations/",
    "/img/sex/",     # 但排除 active
]

todo = []
for n in sorted(set(o) & set(b)):
    so, sb = o[n], b[n]
    if so == sb:
        continue
    short = n.replace("assets/www/", "")
    if "/img/sex/" in n and "/active/" in n:
        continue          # active 目录不动
    if not any(p in n for p in ("/img/transformations/", "/img/sex/")):
        continue
    # 只处理「我们更大」
    if so[0] > sb[0] and so[1] > sb[1]:
        todo.append((short, sb, so))

print("=== 需要修的文件：%d 张 ===" % len(todo))
bydir = defaultdict(list)
for short, sb, so in todo:
    bydir[short.rsplit("/", 1)[0]].append((short.rsplit("/", 1)[-1], sb, so))

for d in sorted(bydir):
    print("\n【%s】%d 张" % (d, len(bydir[d])))
    for fn, sb, so in sorted(bydir[d]):
        print("   %-38s %dx%d -> %dx%d" % (fn, sb[0], sb[1], so[0], so[1]))

# 另外：原版没有、但我们有的（transformations 与 sex/body/transformations 下）
print("\n\n=== 原版没有但我们有的（这两类目录下）===")
extra = []
for n in sorted(set(o) - set(b)):
    if not any(p in n for p in ("/img/transformations/", "/img/sex/")):
        continue
    if "/active/" in n:
        continue
    extra.append((n.replace("assets/www/", ""), o[n]))

if extra:
    bydir2 = defaultdict(list)
    for short, sz in extra:
        bydir2[short.rsplit("/", 1)[0]].append((short.rsplit("/", 1)[-1], sz))
    for d in sorted(bydir2):
        print("\n【%s】%d 张" % (d, len(bydir2[d])))
        for fn, sz in sorted(bydir2[d])[:10]:
            print("   %-38s %dx%d" % (fn, sz[0], sz[1]))
        if len(bydir2[d]) > 10:
            print("   ... 共 %d 张" % len(bydir2[d]))
else:
    print("  无")
