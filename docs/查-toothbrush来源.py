# -*- coding: utf-8 -*-
"""全局搜 toothbrush / soap，找出它们的定义与 props 路径来源。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")
names = z.namelist()

print("=== 1) index 里搜 toothbrush ===")
hits = list(re.finditer(r"toothbrush", h, re.I))
print("命中 %d 处" % len(hits))
for mm in hits[:5]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 400):mm.start() + 400].replace("\n", " ")[:700]))

print("\n\n=== 2) index 里搜 soap（精确词）===")
hits2 = [m for m in re.finditer(r"\bsoap\b", h, re.I)]
print("命中 %d 处" % len(hits2))
for mm in hits2[:5]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 350):mm.start() + 350].replace("\n", " ")[:650]))

print("\n\n=== 3) 文件系统里有没有 toothbrush / soap 的图 ===")
for kw in ("toothbrush", "soap"):
    fs = [n for n in names if kw in n.lower() and n.endswith(".png")]
    print("\n%s: %d 个" % (kw, len(fs)))
    for n in fs[:8]:
        print("   ", n.replace("assets/www/img/", ""))

print("\n\n=== 4) 模组里搜 toothbrush ===")
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
    nm = bj.get("name") or "?"
    for f in zz.namelist():
        if not f.lower().endswith((".js", ".twee", ".json")):
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if re.search(r"toothbrush", t, re.I):
            print("\n[%s] %s" % (nm, f))
            mm = re.search(r"toothbrush", t, re.I)
            print("   ", t[max(0, mm.start() - 300):mm.start() + 400].replace("\n", " ")[:600])
