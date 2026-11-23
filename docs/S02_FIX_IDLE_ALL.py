# -*- coding: utf-8 -*-
"""补齐 Clothes 模组所有 slot 的 idle 图（hands / over_lower / over_upper 等）。"""
import base64
import io
import json
import re
import sys
import zipfile
from collections import defaultdict

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

target = None
for s in parts:
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
    if (bj.get("name") or "") == "Clothes":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到 Clothes")
    sys.exit(1)

s_old, zz, bj = target
names = zz.namelist()

g = defaultdict(set)
for n in names:
    mm = re.match(r"img/clothes/([^/]+)/([^/]+)/(.+)$", n)
    if mm:
        g[(mm.group(1), mm.group(2))].add(mm.group(3))

pairs = []
for (slot, var), files in g.items():
    for side in ("right", "left"):
        if (side + ".png") in files and (side + "-idle.png") not in files:
            base = "img/clothes/%s/%s/" % (slot, var)
            pairs.append((base + side + ".png", base + side + "-idle.png"))

print("需要补:", len(pairs), "个")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
    n = 0
    for src, dst in pairs:
        try:
            data = zz.read(src)
        except KeyError:
            print("  跳过(源不存在):", src)
            continue
        zi = zipfile.ZipInfo(dst, date_time=(2026, 11, 23, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zo.writestr(zi, data)
        n += 1
    print("实际补入:", n)

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
