# -*- coding: utf-8 -*-
"""看 BasicNeeds 里硬编码跳 Orphanage / Bathroom Brush 的上下文。"""
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
    if (bj.get("name") or "") != "BasicNeeds":
        continue
    for f in zz.namelist():
        if not f.lower().endswith((".js", ".twee", ".tw")):
            continue
        try:
            if zz.getinfo(f).file_size > 5_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        for pat in (r"Engine\.play\(\s*['\"]Orphanage['\"]", r"Engine\.play\(\s*['\"]Bathroom Brush['\"]"):
            for mm in re.finditer(pat, t):
                print("\n" + "=" * 66)
                print("【%s】%s  @%d" % (bj.get("name"), f.split("/")[-1], mm.start()))
                print("=" * 66)
                print(t[max(0, mm.start() - 700):mm.start() + 400])
