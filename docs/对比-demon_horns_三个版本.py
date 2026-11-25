# -*- coding: utf-8 -*-
"""只对比 demon/horns 与 cow/horns。"""
import struct
import zipfile

APKS = [
    ("原版", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("AU-F", r"E:\TAML\_dol\apk\对照-AU-F立绘版.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


KEY = "assets/www/img/sex/doggy/body/transformations/demon/"

for label, path in APKS:
    z = zipfile.ZipFile(path)
    names = z.namelist()
    hits = [n for n in names if n.startswith(KEY) and n.endswith(".png")]
    print("\n=== 【%s】demon/  %d 个 ===" % (label, len(hits)))
    for n in sorted(hits):
        d = z.read(n)
        print("  %-42s %-12s %6d" % (n[len(KEY):], png_size(d), len(d)))
