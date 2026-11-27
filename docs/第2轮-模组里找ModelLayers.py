# -*- coding: utf-8 -*-
"""在所有模组里找 ModelLayers 的实例化与 size 定义。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

KEY = ["ModelLayers", "settings.size", "settings = {", "size: ["]

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
    for f in zz.namelist():
        if not f.lower().endswith(".js"):
            continue
        try:
            if zz.getinfo(f).file_size > 5_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if "ModelLayers" not in t:
            continue
        print("\n" + "=" * 72)
        print("【%s】%s  (%d 字符)" % (nm, f.split("/")[-1], len(t)))
        print("=" * 72)
        # 找 size 定义
        for mm in list(re.finditer(r"size\s*:\s*\[[^\]]{1,40}\]", t))[:10]:
            print("   size: %s  @%d" % (mm.group(0), mm.start()))
        # 找 ModelLayers 实例化
        for mm in list(re.finditer(r"ModelLayers", t))[:5]:
            seg = t[max(0, mm.start() - 250):mm.start() + 400]
            print("\n   --- @%d ---" % mm.start())
            print("   " + seg.replace("\n", "\n   ")[:650])
