# -*- coding: utf-8 -*-
r"""修 A 类：同目录内「主流 = 原尺寸，少数被放大」的图，缩回原版尺寸。

为什么只修 A 类：
  A 类（图比主流大）-> downscale，画质无损，且解决「只显示左上 1/4」的错位
  B 类（图比主流小）-> 需要 upscale，会降画质，且只是「显得小」，影响小，暂不动

判据（严格，避免误伤）：
  · 原版该目录内尺寸完全统一（说明该层 canvas 就是这个尺寸）
  · 我们同目录内出现 >=2 种尺寸
  · 该目录主流 = 原版尺寸（x1.00）
  · 该文件 > 主流
  -> 缩放到原版尺寸
"""
import io
import os
import struct
import sys
import zipfile
from collections import Counter, defaultdict

from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
BASE = r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"
OUT = sys.argv[2] if len(sys.argv) > 2 else r"E:\TAML\_dol\work\DoL-sizefix2.apk"


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def load(apk):
    z = zipfile.ZipFile(apk)
    d = {}
    for n in z.namelist():
        if n.startswith("assets/www/img/") and n.endswith(".png"):
            sz = png_size(z.read(n))
            if sz:
                d[n] = sz
    return d


print("加载中...")
o = load(SRC)
b = load(BASE)

bydir_o = defaultdict(dict)
bydir_b = defaultdict(dict)
for n in set(o) & set(b):
    d = n.rsplit("/", 1)[0]
    bydir_o[d][n] = o[n]
    bydir_b[d][n] = b[n]

todo = {}
for d in sorted(bydir_o):
    ob, oo = bydir_b[d], bydir_o[d]
    if len(set(ob.values())) != 1:
        continue
    if len(set(oo.values())) <= 1:
        continue
    base_sz = next(iter(set(ob.values())))
    cnt = Counter(oo.values())
    major, mcount = cnt.most_common(1)[0]
    ratio = major[0] / base_sz[0] if base_sz[0] else 0
    if abs(ratio - 1.0) >= 0.05:
        continue          # 主流不是原尺寸，属 B 类，跳过
    # A 类：把比主流大的缩回主流
    for n, sz in oo.items():
        if sz[0] > major[0] or sz[1] > major[1]:
            todo[n] = major

print("A 类待修：%d 张" % len(todo))

bydir_todo = defaultdict(int)
for n in todo:
    bydir_todo[n.rsplit("/", 1)[0]] += 1
print("\n按目录：")
for d in sorted(bydir_todo, key=lambda x: -bydir_todo[x])[:25]:
    print("  %-58s %d 张" % (d.replace("assets/www/", ""), bydir_todo[d]))
if len(bydir_todo) > 25:
    print("  ... 共 %d 个目录" % len(bydir_todo))

if not todo:
    print("\n无需处理")
    sys.exit(0)

zs = zipfile.ZipFile(SRC)
changed = 0
failed = []
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in zs.infolist():
        fn = info.filename
        data = zs.read(fn)
        if fn in todo:
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                img2 = img.resize(todo[fn], Image.LANCZOS)
                buf = io.BytesIO()
                img2.save(buf, "PNG", optimize=True)
                data = buf.getvalue()
                changed += 1
            except Exception as e:
                failed.append((fn, str(e)))
        zi = zipfile.ZipInfo(fn, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)

print("\n✅ 已缩放 %d 张" % changed)
if failed:
    print("⚠ 失败 %d:" % len(failed))
    for f, e in failed[:5]:
        print("   ", f, e)

print("输出:", OUT, "%.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))

# 校验
z2 = zipfile.ZipFile(OUT)
bad = 0
for n, want in todo.items():
    got = png_size(z2.read(n))
    if got != want:
        bad += 1
        if bad <= 5:
            print("  ❌ %s 得到 %s 期望 %s" % (n.replace("assets/www/", ""), got, want))
print("校验：%d/%d 通过" % (len(todo) - bad, len(todo)))
