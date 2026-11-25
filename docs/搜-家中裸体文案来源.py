# -*- coding: utf-8 -*-
"""在所有模组里搜「反正正是自己家」等文案，定位来源模组。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

KEYS = ["反正正是自己家", "窗帘拉着", "不用提防任何人", "赤脚踩在地板上", "松弛感"]

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
        if not f.lower().endswith((".js", ".twee", ".tw", ".json")):
            continue
        try:
            if zz.getinfo(f).file_size > 5_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        hits = [k for k in KEYS if k in t]
        if not hits:
            continue
        print("\n【%s】%s  命中: %s" % (nm, f.split("/")[-1], hits))
        i = min(t.find(k) for k in hits if t.find(k) >= 0)
        print("  上下文:", t[max(0, i - 600):i + 600].replace("\n", " ")[:1200])
