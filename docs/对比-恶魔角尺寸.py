# -*- coding: utf-8 -*-
"""对比原版/我们的战斗恶魔角尺寸。"""
import os
import re
import struct
import zipfile

APKS = [
    ("原版基础", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("AU-F立绘", r"E:\TAML\_dol\apk\对照-AU-F立绘版.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]

PAT = [
    "demo",
]


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


KEYS = [
    "sex/doggy/body/transformations/demon/horns/default.png",
    "sex/doggy/body/transformations/demon/horns/classic.png",
    "sex/doggy/body/transformations/demon/horns/succubus.png",
    "sex/doggy/body/transformations/demon/horns/front-default.png",
    "sex/doggy/body/transformations/demon/horns/front-succubus.png",
    "sex/doggy/body/transformations/demon/buhorns.png",
    "sex/doggy/body/transformations/demon/horns.png",
]

for label, path in APKS:
    if not os.path.exists(path):
        print("\n【%s】不存在" % label)
        continue
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    print("\n" + "=" * 66)
    print("【%s】" % label)
    print("=" * 66)
    for k in KEYS:
        full = "assets/www/img/" + k
        if full not in names:
            print("  %-52s ❌ 不存在" % k.split("/")[-1])
            continue
        d = z.read(full)
        print("  %-52s %-12s %6d" % (k.split("/")[-1], png_size(d), len(d)))
