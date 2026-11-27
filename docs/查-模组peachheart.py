# -*- coding: utf-8 -*-
"""在模组里搜 peach heart 相关的服装图案定义。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
z = zipfile.ZipFile(APK)
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
    nm = bj.get("name") or "?"
    for f in zz.namelist():
        if not f.lower().endswith((".js", ".twee", ".tw", ".json")):
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if "peach" in t.lower() and "heart" in t.lower():
            print("\n" + "=" * 66)
            print("【%s】%s" % (nm, f.split("/")[-1]))
            print("=" * 66)
            for mm in list(re.finditer(r"peach", t, re.I))[:6]:
                seg = t[max(0, mm.start() - 300):mm.start() + 300]
                if "heart" in seg.lower():
                    print("\n  @%d: %s" % (mm.start(), seg.replace("\n", " ")[:550]))

# 也找所有 pattern_options 里带空格的值（会导致 "-xxx-yyy.png" 拼接）
print("\n\n=== index 里 pattern_options 含空格的值 ===")
for mm in list(re.finditer(r"pattern_options\s*:\s*\[([^\]]{0,600})\]", h)):
    body = mm.group(1)
    items = re.findall(r'"([^"]*)"', body)
    spaced = [x for x in items if " " in x]
    if spaced:
        print("\n  @%d 含空格: %s" % (mm.start(), spaced))
        print("     全部: %s" % items[:15])
