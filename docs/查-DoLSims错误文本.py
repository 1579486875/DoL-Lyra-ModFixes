# -*- coding: utf-8 -*-
"""查 DoLSims 的 Setting Sims.twee 里为何有 JS 错误文本。"""
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
    if (bj.get("name") or "") != "DoLSims":
        continue
    for f in zz.namelist():
        if "Setting Sims" not in f:
            continue
        t = zz.read(f).decode("utf-8", "replace")
        print("=== %s (%d 字符) ===" % (f, len(t)))
        for mm in re.finditer(r"Cannot read properties", t):
            print("\n@%d:" % mm.start())
            print(t[max(0, mm.start() - 800):mm.start() + 600])
    break
