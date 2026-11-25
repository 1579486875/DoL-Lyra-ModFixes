# -*- coding: utf-8 -*-
"""查 maplebirchce.js 里浮层按钮的拖动边界逻辑。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

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
    if (bj.get("name") or "") != "MapleBirchCE":
        continue

    t = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
    print("maplebirchce.js:", len(t), "字节")

    for kw in ("innerWidth", "clientWidth", "innerHeight", "clientHeight",
               "getBoundingClientRect", "mousemove", "touchmove", "pointermove",
               "pageX", "clientX", "zoom", "devicePixelRatio"):
        hits = list(re.finditer(re.escape(kw), t))
        if not hits:
            continue
        print("\n=== %s (%d 处) ===" % (kw, len(hits)))
        for mm in hits[:3]:
            print("  @%d: %s" % (mm.start(), t[max(0, mm.start() - 280):mm.start() + 280].replace("\n", " ")[:520]))
    break
