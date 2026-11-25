# -*- coding: utf-8 -*-
"""查三个翻译问题：
1) 作弊菜单「面部风格: undefined」
2) 「举止: Makeup」未翻译
3) 「狗男's」英文所有格未处理
"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== 1) 面部风格 / facestyle ===")
for kw in ("面部风格", "facestyle", "face_style"):
    hits = list(re.finditer(kw, h))
    print("\n%-14s %d 处" % (kw, len(hits)))
    for mm in hits[:3]:
        print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 250):mm.start() + 250].replace("\n", " ")[:480]))

print("\n\n=== 2) 举止 / Makeup ===")
for kw in ("举止", "Makeup", "makeup"):
    hits = list(re.finditer(kw, h))
    print("\n%-14s %d 处" % (kw, len(hits)))
    for mm in hits[:3]:
        print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 200):mm.start() + 250].replace("\n", " ")[:450]))

print("\n\n=== 3) 狗男 / dogboy ===")
for kw in ("狗男", "dogboy", "dog boy", "'s 的", "的主人"):
    hits = list(re.finditer(kw, h, re.I))
    print("\n%-14s %d 处" % (kw, len(hits)))
    for mm in hits[:3]:
        print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 200):mm.start() + 250].replace("\n", " ")[:450]))
