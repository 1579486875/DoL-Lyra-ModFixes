# -*- coding: utf-8 -*-
"""对比原版/我们的 sex/doggy/body/transformations/ 全部内容。"""
import struct
import zipfile

APKS = [
    ("原版", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


KEY = "assets/www/img/sex/doggy/body/transformations/"

for label, path in APKS:
    z = zipfile.ZipFile(path)
    names = z.namelist()
    hits = [n for n in names if n.startswith(KEY) and n.endswith(".png")]
    print("\n" + "=" * 62)
    print("【%s】sex/doggy/body/transformations/  %d 个" % (label, len(hits)))
    print("=" * 62)
    for n in sorted(hits):
        d = z.read(n)
        rel = n[len(KEY):]
        print("  %-46s %-12s %6d" % (rel, png_size(d), len(d)))
