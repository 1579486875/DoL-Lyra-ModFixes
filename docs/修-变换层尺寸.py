# -*- coding: utf-8 -*-
r"""修 img/transformations/ 下「原版存在但被放大」的图 —— 恶魔角同类问题残留。

判据（严格）：
  · 路径含 /img/transformations/
  · 原版有同名文件（有明确基准尺寸）
  · 我们的宽高都 >= 原版（被放大）
  -> 缩放到原版尺寸

不动的情况：
  · 原版没有的文件（无基准，且多为无 -style 后缀的死文件）
  · img/sex/**（BESC 对 sex 目录做了整体 2 倍升级，canvas 同步升级，正常）
"""
import io
import os
import struct
import sys
import zipfile

from PIL import Image

SRC = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"
OUT = r"E:\TAML\_dol\work\DoL-transfix.apk"


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


base_sizes = {}
zb = zipfile.ZipFile(BASE)
for n in zb.namelist():
    if n.startswith("assets/www/img/transformations/") and n.endswith(".png"):
        sz = png_size(zb.read(n))
        if sz:
            base_sizes[n] = sz

print("原版 img/transformations 图: %d 张" % len(base_sizes))

zs = zipfile.ZipFile(SRC)
todo = []
for n in zs.namelist():
    if not n.startswith("assets/www/img/transformations/") or not n.endswith(".png"):
        continue
    if n not in base_sizes:
        continue
    so = png_size(zs.read(n))
    sb = base_sizes[n]
    if not so:
        continue
    if so == sb:
        continue
    if so[0] >= sb[0] and so[1] >= sb[1]:
        todo.append((n, sb, so))

print("\n=== 待修：%d 张 ===" % len(todo))
for n, sb, so in todo:
    print("   %-58s %dx%d -> %dx%d" % (n.replace("assets/www/", ""), sb[0], sb[1], so[0], so[1]))

if not todo:
    print("无需处理")
    sys.exit(0)

TARGET = {n: sb for n, sb, _ in todo}

changed = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in zs.infolist():
        fn = info.filename
        data = zs.read(fn)
        if fn in TARGET:
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                img2 = img.resize(TARGET[fn], Image.LANCZOS)
                buf = io.BytesIO()
                img2.save(buf, "PNG", optimize=True)
                data = buf.getvalue()
                changed += 1
            except Exception as e:
                print("  ⚠ 失败:", fn, e)
        zi = zipfile.ZipInfo(fn, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)

print("\n✅ 已缩放 %d 张" % changed)
print("输出:", OUT, "%.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))

# 校验
z2 = zipfile.ZipFile(OUT)
print("\n=== 校验 ===")
bad = 0
for n, sb, _ in todo:
    got = png_size(z2.read(n))
    if got != sb:
        print("  ❌ %s 得到 %s 期望 %s" % (n.replace("assets/www/"), got, sb))
        bad += 1
if bad == 0:
    print("  ✅ 全部符合原版尺寸")
