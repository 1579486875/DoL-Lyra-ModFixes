# -*- coding: utf-8 -*-
"""对照原版，确认 demon/horns 各目录的正确尺寸，以及 corset 的真实路径。"""
import struct
import zipfile
from collections import defaultdict

OURS = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def group(apk_path, label):
    z = zipfile.ZipFile(apk_path)
    names = z.namelist()
    bydir = defaultdict(dict)
    for n in names:
        if "demon" in n.lower() and "horn" in n.lower() and n.endswith(".png"):
            sz = png_size(z.read(n))
            d = n.rsplit("/", 1)[0].replace("assets/www/", "")
            bydir[d][n.rsplit("/", 1)[-1]] = sz
    print("\n" + "=" * 72)
    print("【%s】demon/horns 目录" % label)
    print("=" * 72)
    for d in sorted(bydir):
        sizes = defaultdict(int)
        for fn, sz in bydir[d].items():
            sizes[sz] += 1
        summary = ", ".join("%dx%d x%d" % (k[0], k[1], v) if k else "非PNG x%d" % v
                            for k, v in sorted(sizes.items(), key=lambda x: -x[1]))
        print("\n  %s" % d)
        print("     %s" % summary)
    return bydir


o = group(OURS, "我们的包")
b = group(BASE, "原版")

print("\n\n" + "=" * 72)
print("=== 目录级差异（只在一边存在，或尺寸分布不同）===")
print("=" * 72)
alld = sorted(set(o) | set(b))
for d in alld:
    in_o = d in o
    in_b = d in b
    if in_o and not in_b:
        print("\n  [仅我们有] %s" % d)
        for fn, sz in sorted(o[d].items()):
            print("     %-34s %s" % (fn, "%dx%d" % sz if sz else ""))
    elif in_b and not in_o:
        print("\n  [仅原版有] %s" % d)
        for fn, sz in sorted(b[d].items()):
            print("     %-34s %s" % (fn, "%dx%d" % sz if sz else ""))
    else:
        # 两边都有，比同名文件尺寸
        diffs = []
        for fn in sorted(set(o[d]) | set(b[d])):
            so = o[d].get(fn)
            sb = b[d].get(fn)
            if so != sb:
                diffs.append((fn, sb, so))
        if diffs:
            print("\n  [尺寸不同] %s" % d)
            for fn, sb, so in diffs:
                print("     %-34s 原版 %s -> 我们 %s" % (
                    fn,
                    "%dx%d" % sb if sb else "无",
                    "%dx%d" % so if so else "无"))
