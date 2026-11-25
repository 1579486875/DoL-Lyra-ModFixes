# -*- coding: utf-8 -*-
"""对照原版，确定这些目录的正确尺寸。"""
import re
import struct
import zipfile
from collections import defaultdict


def png_size(d):
    if len(d) < 24 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", d[16:24])


APKS = [
    ("原版", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]

# 需要核对的目录 → 关注的文件名
CHECKS = {
    "img/clothes/handheld/paperfan": ["right-idle.png", "right-idle-acc.png", "right-hold.png", "right-cover.png", "right-hold-acc.png"],
    "img/clothes/handheld/parasolpaper": ["right-idle.png", "right-idle-acc.png", "right-hold.png", "right-cover.png"],
    "img/face/default/foxy/red": ["base.png", "eyelids.png", "eyelids-half-closed.png", "eyes.png", "blush-1.png"],
    "img/face/default/gloomy": ["mouthcry.png", "mouthsmile.png", "irisempty-left.png", "sclerabloodshot.png"],
    "img/face/default/gloomy/red": ["base.png", "eyelids.png", "eyes.png", "blush-1.png"],
    "img/face/default/makeup": ["lipstick-chew.png", "sclera-bloodshot.png", "blusher.png"],
    "img/face/default/makeup/red": ["base.png", "eyelids.png", "eyes.png"],
}

for label, path in APKS:
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    print("\n" + "=" * 70)
    print("【%s】" % label)
    print("=" * 70)
    for dirn, files in CHECKS.items():
        print("\n  %s" % dirn)
        for fn in files:
            k = "assets/www/%s/%s" % (dirn, fn)
            if k not in names:
                print("    %-26s ❌ 不存在" % fn)
                continue
            sz = png_size(z.read(k))
            print("    %-26s %s" % (fn, "%dx%d" % sz if sz else "?"))
