# -*- coding: utf-8 -*-
"""修复恶魔角错位：把 BESC 超额尺寸的角图缩放到原版规格。

改动清单：
1) transformations/demon/horns/*.png        : 512x256 -> 256x128
2) sex/doggy/body/transformations/demon/horns/front-classic.png : 1024x256 -> 512x128
3) sex/doggy/body/transformations/demon/horns/{classic,default,succubus}.png : 删除（1024x256 冗余，游戏不读）

保留：
- front-default.png / front-succubus.png 已是 512x128，不动
- back-*.png 已是 512x128，不动
"""
import io
import os
import re
import struct
import zipfile

from PIL import Image

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-hornfix.apk"

z = zipfile.ZipFile(APK)


def png_size(d):
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", d[16:24])


# ---------- 制定计划 ----------
TO_RESIZE = {}   # key -> (target_w, target_h)
TO_DELETE = set()

T1 = "assets/www/img/transformations/demon/horns/"
for n in z.namelist():
    if not n.startswith(T1) or not n.endswith(".png"):
        continue
    sz = png_size(z.read(n))
    if sz == (512, 256):
        TO_RESIZE[n] = (256, 128)

T2 = "assets/www/img/sex/doggy/body/transformations/demon/horns/"
for n in z.namelist():
    if not n.startswith(T2) or not n.endswith(".png"):
        continue
    base = n[len(T2):]
    sz = png_size(z.read(n))
    if base in ("classic.png", "default.png", "succubus.png") and sz == (1024, 256):
        TO_DELETE.add(n)
    elif sz == (1024, 256):
        TO_RESIZE[n] = (512, 128)

print("=== 计划 ===")
print("缩放:", len(TO_RESIZE))
for k, v in sorted(TO_RESIZE.items()):
    print("  %-62s -> %dx%d" % (k.replace("assets/www/img/", ""), v[0], v[1]))
print("删除:", len(TO_DELETE))
for k in sorted(TO_DELETE):
    print("  ", k.replace("assets/www/img/", ""))

# ---------- 重建 ----------
changed = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        fn = info.filename
        if fn in TO_DELETE:
            continue
        data = z.read(fn)
        if fn in TO_RESIZE:
            tw, th = TO_RESIZE[fn]
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            img2 = img.resize((tw, th), Image.LANCZOS)
            buf = io.BytesIO()
            img2.save(buf, "PNG", optimize=True)
            data = buf.getvalue()
            changed += 1
        zi = zipfile.ZipInfo(fn, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)

print("\n✅ 缩放 %d 个，删除 %d 个" % (changed, len(TO_DELETE)))
print("输出:", OUT, "%.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))

# ---------- 校验 ----------
z2 = zipfile.ZipFile(OUT)
print("\n=== 校验 ===")
print("条目数: %d (原 %d)" % (len(z2.namelist()), len(z.namelist())))
for n in sorted(z2.namelist()):
    if n.startswith(T1) and n.endswith(".png"):
        print("  %-42s %s" % (n[len(T1):], png_size(z2.read(n))))
