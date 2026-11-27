# -*- coding: utf-8 -*-
"""看 TweeReplacer patch 的真实字段名。"""
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
    if nm != "FertilityExpansion":
        continue
    for p in (bj.get("addonPlugin") or []):
        if not isinstance(p, dict):
            continue
        if "TweeReplacer" not in (p.get("modName") or ""):
            continue
        print("=== FertilityExpansion / TweeReplacer ===")
        print("  addonPlugin 的键:", list(p.keys()))
        params = p.get("params")
        print("  params 类型:", type(params).__name__)
        if isinstance(params, dict):
            print("  params 的键:", list(params.keys()))
            for k, v in params.items():
                print("    %s: %s (len=%d)" % (k, type(v).__name__, len(v) if hasattr(v, '__len__') else -1))
                if isinstance(v, list) and v:
                    print("      第一条的键:", list(v[0].keys()) if isinstance(v[0], dict) else type(v[0]).__name__)
                    print("      第一条内容:", json.dumps(v[0], ensure_ascii=False)[:400])
        elif isinstance(params, list) and params:
            print("  第一条的键:", list(params[0].keys()) if isinstance(params[0], dict) else "?")
            print("  第一条内容:", json.dumps(params[0], ensure_ascii=False)[:400])
    break
