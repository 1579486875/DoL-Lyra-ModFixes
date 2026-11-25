# -*- coding: utf-8 -*-
"""看 Cheat Face Fix 的完整实现。"""
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
    if (bj.get("name") or "") != "Cheat Face Fix":
        continue
    print("=== Cheat Face Fix 文件 ===")
    for n in zz.namelist():
        print("  ", n)
    print("\n=== boot.json ===")
    print(json.dumps(bj, ensure_ascii=False, indent=1)[:800])
    for n in zz.namelist():
        if n.endswith(".js"):
            t = zz.read(n).decode("utf-8", "replace")
            print("\n=== %s (%d 字符) ===" % (n, len(t)))
            print(t)
    break
