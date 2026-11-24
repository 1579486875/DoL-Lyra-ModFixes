# -*- coding: utf-8 -*-
"""系统排查：所有 passage 被哪些模组 patch，找出锚点冲突。"""
import base64
import html as H
import io
import json
import re
import zipfile
from collections import defaultdict

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")

# 1) 取所有 passage 原文
PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PS[m.group(1)] = H.unescape(m.group(2))

# 2) 收集所有 patch
patches = []   # (mod, plugin, passage, findType, findStr, replaceFile)
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
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
    mod = bj.get("name") or "?"

    for p in (bj.get("addonPlugin") or []):
        if not isinstance(p, dict):
            continue
        pname = p.get("modName") or ""
        if "TweeReplacer" not in pname and "ReplacePatcher" not in pname:
            continue
        params = p.get("params")
        items = params if isinstance(params, list) else (
            [x for v in params.values() if isinstance(v, list) for x in v] if isinstance(params, dict) else [])
        for par in items:
            if not isinstance(par, dict):
                continue
            passage = par.get("passage") or par.get("passageName")
            if not passage:
                continue
            find = par.get("findString") or par.get("findRegex") or par.get("from") or ""
            rf = par.get("replaceFile") or par.get("replace") or par.get("to") or ""
            patches.append((mod, pname, passage, len(find), str(find), str(rf)))

print("=== 一、patch 总览 ===")
print("总 patch 数:", len(patches))

# 3) 按 passage 分组
by_passage = defaultdict(list)
for x in patches:
    by_passage[x[2]].append(x)

# 4) 找出被 2+ 个模组 patch 的 passage
print("\n=== 二、被多个模组 patch 的 passage ===")
multi = {k: v for k, v in by_passage.items() if len(set(x[0] for x in v)) >= 2}
for passage in sorted(multi, key=lambda k: -len(multi[k])):
    v = multi[passage]
    mods = sorted(set(x[0] for x in v))
    exists = passage in PS
    print("\n【%s】%d 条 patch，%d 个模组%s" % (
        passage, len(v), len(mods), "" if exists else "  ⚠️ passage 不存在"))
    print("   模组:", mods)
    # 找相同/相似的 find
    finds = defaultdict(list)
    for mod, pname, ps, flen, find, rf in v:
        key = find.strip()[:60]
        finds[key].append(mod)
    for k, mods2 in finds.items():
        if len(set(mods2)) >= 2:
            print("   ⚠️ 同一锚点被多个模组使用:", set(mods2))
            print("      锚点:", k[:80])
