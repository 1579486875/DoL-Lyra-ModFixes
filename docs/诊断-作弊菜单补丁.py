# -*- coding: utf-8 -*-
"""诊断：CHEAT_FACE_FIX 为什么没生效。

检查：
1) 补丁是否真的在包里
2) 目标 DOM 选择器 #statsFaceStyle / #statsDemeanour 是否存在于作弊菜单
3) 作弊菜单的实际 DOM 结构
"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

print("=== 1) 补丁是否在包里 ===")
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
    if (bj.get("name") or "") != "系统联动补全":
        continue
    t = zz.read("scripts/core.js").decode("utf-8", "replace")
    for k in ("CHEAT_FACE_FIX", "cheatFaceFix", "ARTICLE_FIX", "articleFix", "POSSESSIVE_FIX", "PROP_FOLDER_FIX", "inOwnHome 修正版"):
        print("  %-24s %s" % (k, "✅" if k in t else "❌"))
    break

print("\n=== 2) 作弊菜单里的目标 DOM 结构 ===")
# 找 statsFaceStyle / statsDemeanour / cheatsFaceStyle 相关
for kw in ("statsFaceStyle", "statsDemeanour", "cheatsFaceStyle", "cheatsDemeanour"):
    hits = list(re.finditer(kw, h))
    print("\n%s: %d 处" % (kw, len(hits)))
    for mm in hits[:2]:
        print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 350):mm.start() + 350].replace("\n", " ")[:700]))

print("\n=== 3) faceStyleOptions / faceVariantOptions ===")
for kw in ("faceStyleOptions", "faceVariantOptions"):
    hits = list(re.finditer(kw, h))
    print("\n%s: %d 处" % (kw, len(hits)))
    for mm in hits[:3]:
        print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 200):mm.start() + 400].replace("\n", " ")[:600]))
