# -*- coding: utf-8 -*-
"""查 BasicNeeds 装水功能（fillPick / bnFillPick）的入口，看它是否只在孤儿院。"""
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
        # 找 fillWater 场景 / 饮水机入口
        for kw in ("BasicNeeds Fill Water", "fillWaterScene", "bnFillPick", "饮水机", "fillPick"):
            for mm in list(re.finditer(re.escape(kw), t))[:2]:
                print("\n" + "=" * 66)
                print("【%s】%s  %s @%d" % (bj.get("name"), f.split("/")[-1], kw, mm.start()))
                print("=" * 66)
                print(t[max(0, mm.start() - 450):mm.start() + 450].replace("\n", "\n"))
