# -*- coding: utf-8 -*-
"""读 Ban-needs.js，找需求满的处理、失禁、对外钩子。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
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
    t = zz.read("scripts/Ban-needs.js").decode("utf-8", "replace")

    # 1) 所有函数名
    print("=== 定义的函数 ===")
    fns = sorted(set(re.findall(r"(?:function\s+|^\s*)([a-zA-Z_]\w*)\s*[:=]\s*(?:function|\()", t, re.M)))
    print("  ", ", ".join(fns[:40]))

    # 2) 失禁/意外
    print("\n=== 失禁 / 意外相关 ===")
    for kw in ("accident", "soiled", "wetself", "overflow", "burst", "relieve", "toilet"):
        ms = list(re.finditer(kw, t, re.I))
        if ms:
            mm = ms[0]
            print("  %-12s %2d 次 | %s" % (kw, len(ms), repr(t[max(0, mm.start() - 120):mm.start() + 180])[:300]))

    # 3) 满值判定
    print("\n=== 满值判定（>= 阈值）===")
    for mm in list(re.finditer(r"(\w+)\s*>=\s*(?:1|0?\.\d+|\w+\.max|max)", t))[:12]:
        print("   ", repr(t[max(0, mm.start() - 80):mm.start() + 120])[:240])

    # 4) 对外联动（调用其他系统）
    print("\n=== 对外调用（跨系统）===")
    for kw in ("V.exhibitionism", "exhibitionism", "mee.", "maplebirch", "FertilityExpansion", "pregnancy", "enemyarousal"):
        ms = list(re.finditer(re.escape(kw), t))
        if ms:
            print("  %-22s %d 次" % (kw, len(ms)))
            mm = ms[0]
            print("     ", repr(t[max(0, mm.start() - 100):mm.start() + 140])[:260])
    break
