# -*- coding: utf-8 -*-
"""第2轮：全量检查 TweeReplacer / ReplacePatcher 的锚点在 index 中是否命中。"""
import base64
import html as H
import io
import json
import re
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(raw)

# 建立 passage 名 -> body 的映射
PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PS[m.group(1)] = m.group(2)
print("passages:", len(PS))

# 提取全部模组 ZIP
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
mods = []
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
        mods.append((bj.get("name"), bj.get("version"), zz))
    except Exception:
        continue
print("mods:", len(mods))

miss_total = 0
for name, ver, zz in mods:
    miss = []
    for a in (json.loads(zz.read("boot.json").decode("utf-8-sig")).get("addonPlugin") or []):
        if a.get("addonName") != "TweeReplacerAddon":
            continue
        ps = a.get("params")
        if not isinstance(ps, list):
            continue
        for pt in ps:
            if not isinstance(pt, dict):
                continue
            passage = pt.get("passage")
            fs = pt.get("findString")
            if not passage or fs is None:
                continue
            body = PS.get(passage)
            if body is None:
                miss.append((passage, "PASSAGE_MISSING", ""))
                continue
            if fs not in body:
                miss.append((passage, "FIND_MISSING", fs[:80]))
    if miss:
        miss_total += len(miss)
        print("\n[%s %s] 失配 %d 条" % (name, ver, len(miss)))
        for p, kind, snippet in miss[:6]:
            print("   %-32s %-14s %s" % (p, kind, snippet.replace("\n", "\\n")))

print("\n总失配:", miss_total)
