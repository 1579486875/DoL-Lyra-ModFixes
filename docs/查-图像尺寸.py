# -*- coding: utf-8 -*-
"""检查三类问题服装所有图的尺寸，找出所有 256x128 的旧资源。"""
import struct
import zipfile
from collections import defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


TARGETS = [
    "under-upper/corset",
    "upper/succubus",
    "lower/succubus",
    "upper/cardigan sailor uniform",
    "lower/cardigan sailor uniform",
    "lower/serafuku_dress",
    "lower/serafuku-dress",
]

for ti in TARGETS:
    prefix = "assets/www/img/clothes/%s/" % ti
    files = [(n[len(prefix):-4], n) for n in z.namelist() if n.startswith(prefix) and n.endswith(".png")]
    if not files:
        continue
    sizes = defaultdict(list)
    for label, k in files:
        sz = png_size(z.read(k))
        sizes[sz].append(label)
    print("\n【%s】%d 个文件" % (ti, len(files)))
    for sz, labels in sorted(sizes.items(), key=lambda x: -len(x[1])):
        print("   %s : %d 个  %s" % (sz, len(labels), labels[:8]))
