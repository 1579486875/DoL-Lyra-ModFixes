# -*- coding: utf-8 -*-
"""保守修复：只处理 img/clothes/handheld/ 下的尺寸不一致（手持物用户能直接看到）。

不发散到所有服装 —— 数百张图整体缩放会降低画质，且难以逐张验证。
"""
import io
import os
import re
import struct
import zipfile
from collections import Counter, defaultdict

from PIL import Image

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-handheld-sizefix.apk"
PREFIX = "assets/www/img/clothes/handheld/"


def png_size(d):
    if len(d) < 24 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", d[16:24])


def family(fn):
    base = fn[:-4]
    m = re.match(r"^(right-idle|right-hold|right-cover|right|left-idle|left-hold|left-cover|left|back)", base)
    if m:
        return m.group(1)
    return base.split("-")[0]


z = zipfile.ZipFile(APK)
by_dir = defaultdict(list)
for n in z.namelist():
    if not n.startswith(PREFIX) or not n.endswith(".png"):
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
        if cnt.get((512, 256), 0) >= 1 and cnt.get((256, 128), 0) >= 1:
            for n, sz in items:
                if sz == (256, 128):
                    TODO.setdefault(d, []).append((n, fam))

print("=== handheld 下待处理 ===")
total = 0
for d in sorted(TODO):
    fams = sorted({f for _, f in TODO[d]})
    print("  %-56s %2d 张  族=%s" % (d.replace("assets/www/", ""), len(TODO[d]), fams))
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
ok = 0
for d in sorted(TODO):
    left = []
    for n, fam in TODO[d]:
        sz = png_size(z2.read(n))
        if sz != (512, 256):
            left.append((n.rsplit("/", 1)[-1], sz))
    if left:
        print("  ❌ %-50s %s" % (d.replace("assets/www/", ""), left[:3]))
    else:
        ok += 1
        print("  ✅ %-50s" % d.replace("assets/www/", ""))
print("\n通过 %d / %d" % (ok, len(TODO)))
