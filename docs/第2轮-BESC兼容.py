# -*- coding: utf-8 -*-
"""第2轮：BESC 补全后的兼容性检查。

1) 新增文件是否覆盖了原有文件（应该没有，因只补缺失）
2) 关键图层尺寸是否一致（breasts0-6 应该是 512x256）
3) 是否有重复条目
"""
import re
import struct
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
names = z.namelist()

print("=== 1. 重复条目检查 ===")
dup = [k for k, v in Counter(names).items() if v > 1]
print("重复条目:", len(dup))
for d in dup[:10]:
    print("   ", d)

print("\n=== 2. 关键图层尺寸 ===")


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", data[16:24])
    return (w, h)


KEY = [
    "assets/www/img/body/breasts/breasts%d.png" % i for i in range(0, 7)
] + [
    "assets/www/img/body/base-curvy.png",
    "assets/www/img/body/basenoarms-f.png",
]
for k in KEY:
    if k not in names:
        print("   ❌ %-52s 不存在" % k)
        continue
    data = z.read(k)
    size = png_size(data)
    print("   %-52s %s  %d bytes" % (k.split("/")[-1], size, len(data)))

print("\n=== 3. 新增文件占比 ===")
img_all = [n for n in names if n.startswith("assets/www/img/") and n.endswith(".png")]
print("img PNG 总数:", len(img_all))

print("\n=== 4. 检查 body/breasts 全系列 ===")
for prefix in ("breasts", "breastsparasite", "chestparasite", "chestslime"):
    got = []
    for i in range(0, 7):
        k = "assets/www/img/body/breasts/%s%d.png" % (prefix, i)
        got.append(i if k in names else None)
    print("   %-18s 有: %s" % (prefix, [x for x in got if x is not None]))
