# -*- coding: utf-8 -*-
"""确认 Handheld Idle Fix / Face Variant Fill 里哪些图尺寸错了。

判据：同一目录下「同名前缀」的图应该同尺寸。
例如 paperfan/right-idle.png 应该和 paperfan/right-hold.png 同尺寸。
"""
import base64
import io
import json
import re
import struct
import zipfile
from collections import defaultdict


def png_size(d):
    if len(d) < 24 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", d[16:24])


APK = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = APK.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

TARGET_MODS = ["Handheld Idle Fix", "Face Variant Fill"]

for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    nm = bj.get("name") or ""
    if nm not in TARGET_MODS:
        continue

    print("\n" + "=" * 70)
    print("【%s】" % nm)
    print("=" * 70)

    imgs = [f for f in (bj.get("imgFileList") or []) if isinstance(f, str)]
    # 按目录分组，列出每个文件尺寸
    by_dir = defaultdict(list)
    for f in imgs:
        if f not in zz.namelist():
            continue
        sz = png_size(zz.read(f))
        if not sz:
            continue
        dirn = f.rsplit("/", 1)[0]
        by_dir[dirn].append((f.rsplit("/", 1)[-1], sz))

    for dirn in sorted(by_dir):
        files = by_dir[dirn]
        sizes = defaultdict(list)
        for fn, sz in files:
            sizes[sz].append(fn)
        if len(sizes) < 2:
            continue
        print("\n  %s  （%d 个文件，%d 种尺寸）" % (dirn, len(files), len(sizes)))
        for sz, fns in sorted(sizes.items(), key=lambda x: -len(x[1])):
            print("    %dx%d : %d 个" % (sz[0], sz[1], len(fns)))
            for f in fns[:6]:
                print("       ", f)
