# -*- coding: utf-8 -*-
"""查游戏的「缩放」是怎么实现的：CSS zoom / transform scale / 还是 viewport。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== index.html 里的 zoom / scale 用法 ===")
for kw in ("zoom:", "scale(", "--game-zoom", "gameZoom", "document.body.style.zoom"):
    hits = list(re.finditer(re.escape(kw), h))
    print("\n%-24s %d 处" % (kw, len(hits)))
    for mm in hits[:2]:
        print("   @%d: %s" % (mm.start(), h[max(0, mm.start() - 200):mm.start() + 220].replace("\n", " ")[:400]))

# ModLoaderGui 的缩放配置
print("\n\n=== ModLoaderGui 里的缩放实现 ===")
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
    nm = bj.get("name") or ""
    for f in zz.namelist():
        if not f.lower().endswith(".js"):
            continue
        try:
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if "zoom" not in t.lower():
            continue
        for kw in ("style.zoom", "transform", "zoom =", "zoom:"):
            for mm in list(re.finditer(re.escape(kw), t))[:2]:
                print("\n[%s] %s @%d" % (nm, kw, mm.start()))
                print("   " + t[max(0, mm.start() - 250):mm.start() + 250].replace("\n", " ")[:480])
