# -*- coding: utf-8 -*-
"""检查每个 patch 的 findString 是否还在 passage 里（失效=该 patch 不会生效）。"""
import base64
import html as H
import io
import json
import re
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")

PS = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PS[m.group(1)] = H.unescape(m.group(2))

mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
dead = []
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
        pname = p.get("modName") or ""
        if "TweeReplacer" not in pname:
            continue
        params = p.get("params")
        items = params if isinstance(params, list) else (
            [x for v in params.values() if isinstance(v, list) for x in v] if isinstance(params, dict) else [])
        for par in items:
            if not isinstance(par, dict):
                continue
            passage = par.get("passage") or par.get("passageName")
            find = par.get("findString")
            fre = par.get("findRegex")
            if not passage or (not find and not fre):
                continue
            total += 1

            body = PS.get(passage)
            if body is None:
                dead.append((mod, passage, "PASSAGE_MISSING", str(find or fre)[:70]))
                continue

            ok = False
            try:
                if find:
                    ok = (find in body)
                elif fre:
                    ok = re.search(fre, body) is not None
            except Exception as e:
                ok = False

            if not ok:
                dead.append((mod, passage, "ANCHOR_MISSING", str(find or fre).replace("\n", " ")[:70]))

print("总 patch:", total)
print("失效 patch:", len(dead))
print("=" * 78)
from collections import defaultdict
g = defaultdict(list)
for mod, ps, kind, anchor in dead:
    g[mod].append((ps, kind, anchor))
for mod in sorted(g, key=lambda k: -len(g[k])):
    print("\n【%s】%d 条失效" % (mod, len(g[mod])))
    for ps, kind, anchor in g[mod][:8]:
        print("   %-38s %-14s %s" % (ps, kind, anchor))
