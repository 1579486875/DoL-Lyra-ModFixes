# -*- coding: utf-8 -*-
"""详查空壳/半成品模组的实际内容。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

WATCH = ["Face Variant Fill", "Handheld Idle Fix", "Npc Name CN", "Stat Name CN",
         "BeautySelectorAddon", "ConflictChecker", "Diff3WayMerge",
         "CheckGameVersion", "I18nScriptList", "I18nTweeList", "ImageLoaderHook2BeautySelect",
         "CheckDoLCompressorDictionaries", "Cheat Face Fix"]

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
    if nm not in WATCH:
        continue
    print("\n" + "=" * 66)
    print("【%s】v%s" % (nm, bj.get("version")))
    print("=" * 66)
    print("  描述:", str(bj.get("description") or "")[:180])
    print("  文件:", zz.namelist())
    for f in ("scriptFileList", "tweeFileList", "styleFileList", "imgFileList", "addonPlugin"):
        v = bj.get(f) or []
        if v:
            print("  %-16s %s" % (f, str(v)[:200]))
    # 如果有 js 文件，看内容
    for n in zz.namelist():
        if n.endswith(".js"):
            t = zz.read(n).decode("utf-8", "replace")
            print("  --- %s (%d 字符) ---" % (n, len(t)))
            print("  " + t[:600].replace("\n", "\n  "))
