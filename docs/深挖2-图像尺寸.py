# -*- coding: utf-8 -*-
"""深挖2：扫所有模组提供的图片，找「同一目录下尺寸不一致」的情况。

恶魔角的问题就是：一个目录里既有 512x128 又有 1024x256，
渲染器按固定尺寸绘制 → 大尺寸图只画左上 1/4 → 错位。

判据：同一个目录下，同名模式的文件出现 ≥2 种尺寸，且其中一种占多数。
"""
import base64
import io
import json
import re
import struct
import zipfile
from collections import Counter, defaultdict


def png_size(d):
    if len(d) < 24 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", d[16:24])


z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

issues = []
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
    nm = bj.get("name") or "?"
    imgs = bj.get("imgFileList") or []
    if not imgs:
        continue

    # 按目录聚合
    by_dir = defaultdict(list)
    for f in imgs:
        if not isinstance(f, str) or not f.endswith(".png"):
            continue
        if f not in zz.namelist():
            continue
        sz = png_size(zz.read(f))
        if not sz:
            continue
        d_ = f.rsplit("/", 1)[0] if "/" in f else "(根)"
        by_dir[d_].append((f, sz))

    for dirname, files in by_dir.items():
        if len(files) < 3:
            continue
        cnt = Counter(sz for _, sz in files)
        if len(cnt) < 2:
            continue
        # 占多数的尺寸
        major, mcount = cnt.most_common(1)[0]
        odd = [(f, sz) for f, sz in files if sz != major]
        if not odd:
            continue
        # 只看「明显不同」（面积比 >1.8 或 <0.55）
        real_odd = []
        for f, sz in odd:
            a = sz[0] * sz[1]
            b = major[0] * major[1]
            if b == 0:
                continue
            r = a / b
            if r > 1.8 or r < 0.55:
                real_odd.append((f, sz))
        if real_odd:
            issues.append((nm, dirname, major, mcount, len(files), real_odd))

print("=== 疑似尺寸错配 ===")
print("共 %d 组" % len(issues))
for nm, dirname, major, mcount, total, odd in issues:
    print("\n【%s】%s" % (nm, dirname))
    print("  主流尺寸 %dx%d（%d/%d），异常 %d 个:" % (major[0], major[1], mcount, total, len(odd)))
    for f, sz in odd[:8]:
        print("     %-46s %dx%d" % (f.rsplit("/", 1)[-1], sz[0], sz[1]))
    if len(odd) > 8:
        print("     ... 共 %d 个" % len(odd))
