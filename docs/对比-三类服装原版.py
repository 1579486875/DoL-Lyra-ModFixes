# -*- coding: utf-8 -*-
"""对比原版 / 我们：三类问题服装的尺寸与大小。"""
import os
import struct
import zipfile

APKS = [
    ("原版基础", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("我们(BESC)", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]

TARGETS = [
    "under-upper/corset",
    "upper/succubus",
    "lower/succubus",
    "upper/cardigan sailor uniform",
    "lower/cardigan sailor uniform",
]


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


for label, path in APKS:
    if not os.path.exists(path):
        print("\n【%s】不存在" % label)
        continue
    z = zipfile.ZipFile(path)
    print("\n" + "=" * 60)
    print("【%s】" % label)
    print("=" * 60)
    for ti in TARGETS:
        prefix = "assets/www/img/clothes/%s/" % ti
        files = [n for n in z.namelist() if n.startswith(prefix) and n.endswith(".png")]
        if not files:
            print("  %-32s ❌ 无文件" % ti)
            continue
        # 只统计数字变体 + full
        stat = {}
        for n in files:
            b = n[len(prefix):-4]
            if b.isdigit() or b == "full":
                data = z.read(n)
                stat[b] = (png_size(data), len(data))
        line = "  %-32s " % ti
        parts = []
        for k in ["0", "1", "2", "3", "4", "5", "6", "full"]:
            if k in stat:
                sz, ln = stat[k]
                parts.append("%s=%s/%dB" % (k, "512" if sz == (512, 256) else ("256" if sz == (256, 128) else str(sz)), ln))
        print(line + " | ".join(parts) if parts else line + "(无数字/full)")
