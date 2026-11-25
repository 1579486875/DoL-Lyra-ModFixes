# -*- coding: utf-8 -*-
"""精化判据：只修「同一图层族（同前缀）内尺寸不一致」的图。

图层族定义：把文件名末尾的「-变体后缀」去掉得到前缀。
  例如 right-idle.png / right-idle-apricots.png / right-idle-cranes.png
  都归到族 "right-idle"

只有当同一族里既有 512x256 又有 256x128 时，才把 256x128 的放大到 512x256。
这样不会误伤 img/body 那种「不同图层本来就不同尺寸」的目录。
"""
import io
import os
import re
import struct
import zipfile
from collections import Counter, defaultdict

from PIL import Image

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-sizefix.apk"


def png_size(d):
    if len(d) < 24 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", d[16:24])


def family(fn):
    """把文件名归到一个「图层族」。"""
    base = fn[:-4]
    # 去掉常见变体后缀：-xxx（连字符），但保留前缀里的连字符
    m = re.match(r"^(right-idle|right-hold|right-cover|right|left-idle|left-hold|left-cover|left)", base)
    if m:
        return m.group(1)
    # 其他：取第一个连字符前
    return base.split("-")[0]


z = zipfile.ZipFile(APK)
by_dir = defaultdict(list)
for n in z.namelist():
    if not n.startswith("assets/www/img/") or not n.endswith(".png"):
        continue
    sz = png_size(z.read(n))
    if not sz:
        continue
    by_dir[n.rsplit("/", 1)[0]].append((n, sz))

TODO = {}
for d, files in by_dir.items():
    fams = defaultdict(list)
    for n, sz in files:
        fams[family(n.rsplit("/", 1)[-1])].append((n, sz))
    for fam, items in fams.items():
        if len(items) < 2:
            continue
        cnt = Counter(sz for _, sz in items)
        big = cnt.get((512, 256), 0)
        small = cnt.get((256, 128), 0)
        # 只有同族里两种尺寸都出现，且大的 >=1、小的 >=1 才处理
        if big >= 1 and small >= 1:
            for n, sz in items:
                if sz == (256, 128):
                    TODO.setdefault(d, []).append((n, fam))

print("=== 精确待处理（同族尺寸不一致）===")
total = 0
for d in sorted(TODO):
    fams = sorted({f for _, f in TODO[d]})
    print("  %-52s %2d 张  族=%s" % (d.replace("assets/www/", ""), len(TODO[d]), fams))
    total += len(TODO[d])
print("合计: %d 张" % total)

if total == 0:
    print("无需处理")
    raise SystemExit(0)

TARGET = {n for lst in TODO.values() for n, _ in lst}

changed = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in z.infolist():
        fn = info.filename
        data = z.read(fn)
        if fn in TARGET:
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                img2 = img.resize((512, 256), Image.LANCZOS)
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

z2 = zipfile.ZipFile(OUT)
print("\n=== 校验 ===")
for d in sorted(TODO):
    left = []
    for n, fam in TODO[d]:
        sz = png_size(z2.read(n))
        if sz != (512, 256):
            left.append((n.rsplit("/", 1)[-1], sz))
    print("  %-52s %s" % (d.replace("assets/www/", ""), "✅" if not left else "❌ " + str(left[:3])))
