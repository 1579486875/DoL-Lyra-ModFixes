# -*- coding: utf-8 -*-
"""深挖2修复：把 handheld / face 目录里尺寸不一致的图统一到 512x256。

依据：
  #player-body 的 CSS width 是 256px，但 canvas 内部是 512x256（BESC 升级），
  浏览器按 2 倍缩小显示。若某张图只有 256x128，只占左上 1/4 → 错位。

处理范围（只碰 BESC 已升级到 512x256 的目录）：
  img/clothes/handheld/*        : 256x128 -> 512x256
  img/face/default/{foxy,gloomy,makeup}*/ : 按目录主流尺寸统一

注意：不碰原版就是统一 256x128 的目录（例如未被 BESC 升级的）。
"""
import io
import os
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


z = zipfile.ZipFile(APK)
names = z.namelist()

# 按目录聚合 APK 内所有 img
by_dir = defaultdict(list)
for n in names:
    if not n.startswith("assets/www/img/") or not n.endswith(".png"):
        continue
    sz = png_size(z.read(n))
    if not sz:
        continue
    d = n.rsplit("/", 1)[0]
    by_dir[d].append((n, sz))

# 判定「该目录应该统一到 512x256」：
#   - 目录里有 >=3 个 512x256
#   - 且存在 256x128
TODO = {}
for d, files in by_dir.items():
    cnt = Counter(sz for _, sz in files)
    big = cnt.get((512, 256), 0)
    small = cnt.get((256, 128), 0)
    if big >= 2 and small >= 1:
        TODO[d] = [(n, sz) for n, sz in files if sz == (256, 128)]

print("=== 待处理目录 ===")
total = 0
for d in sorted(TODO):
    print("  %-52s %d 张 256x128 -> 512x256" % (d.replace("assets/www/", ""), len(TODO[d])))
    total += len(TODO[d])
print("合计: %d 张" % total)

if total == 0:
    print("无需处理")
    raise SystemExit(0)

# 执行
changed = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in z.infolist():
        fn = info.filename
        data = z.read(fn)
        if fn in {n for lst in TODO.values() for n, _ in lst}:
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                img2 = img.resize((512, 256), Image.LANCZOS)
                buf = io.BytesIO()
                img2.save(buf, "PNG", optimize=True)
                data = buf.getvalue()
                changed += 1
            except Exception as e:
                print("  ⚠ 处理失败:", fn, e)
        zi = zipfile.ZipInfo(fn, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)

print("\n✅ 已缩放 %d 张" % changed)
print("输出:", OUT, "%.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))

# 校验
z2 = zipfile.ZipFile(OUT)
print("\n=== 校验 ===")
for d in sorted(TODO)[:6]:
    left = [(n, png_size(z2.read(n))) for n, _ in TODO[d]]
    bad = [(n.rsplit("/", 1)[-1], s) for n, s in left if s != (512, 256)]
    print("  %-52s %s" % (d.replace("assets/www/", ""), "✅ 全部 512x256" if not bad else "❌ " + str(bad[:3])))
