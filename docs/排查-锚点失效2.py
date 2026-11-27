# -*- coding: utf-8 -*-
r"""锚点失效检查（支持传 APK 或 index 路径）。

用法：
  python 排查-锚点失效2.py                    # 默认 work\index_modded6.html
  python 排查-锚点失效2.py <apk>              # 检查某个 APK 内的 index
  python 排查-锚点失效2.py <apk> --summary    # 只输出总数
"""
import base64
import html as H
import io
import json
import re
import sys
import zipfile

TARGET = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\work\index_modded6.html"
SUMMARY = "--summary" in sys.argv


def read_index(p):
    if p.lower().endswith(".apk"):
        z = zipfile.ZipFile(p)
        return z.read("assets/www/index.html").decode("utf-8", "replace")
    return open(p, "rb").read().decode("utf-8", "replace")


raw = read_index(TARGET)

PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PS[m.group(1)] = H.unescape(m.group(2))

mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
if not mz:
    print("找不到 modDataValueZipList")
    sys.exit(1)

dead_by_mod = {}
total = 0

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
        if "TweeReplacer" not in (p.get("modName") or ""):
            continue
        params = p.get("params")
        items = params if isinstance(params, list) else (
            [x for v in params.values() if isinstance(v, list) for x in v] if isinstance(params, dict) else [])
        for par in items:
            if not isinstance(par, dict):
                continue
            total += 1
            pname = par.get("passageName") or par.get("passage") or ""
            find = par.get("findString") or par.get("find") or ""
            if not pname or not find:
                continue
            body = PS.get(pname)
            if body is None:
                dead_by_mod.setdefault(mod, []).append((pname, "PASSAGE_MISSING", find[:80]))
            elif find not in body:
                dead_by_mod.setdefault(mod, []).append((pname, "ANCHOR_MISSING", find[:80]))

dead_total = sum(len(v) for v in dead_by_mod.values())

if SUMMARY:
    print("%s: patch=%d dead=%d" % (TARGET.split("\\")[-1], total, dead_total))
else:
    print("目标: %s" % TARGET)
    print("总 patch: %d" % total)
    print("失效 patch: %d" % dead_total)
    print("=" * 70)
    for mod in sorted(dead_by_mod, key=lambda x: -len(dead_by_mod[x])):
        items = dead_by_mod[mod]
        print("\n【%s】%d 条失效" % (mod, len(items)))
        for pn, why, f in items[:6]:
            print("   %-40s %-16s %s" % (pn[:38], why, f.replace("\n", " ")[:70]))
        if len(items) > 6:
            print("   ... 共 %d" % len(items))
