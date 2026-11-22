# -*- coding: utf-8 -*-
"""在 index 的全部模组 ZIP 里搜繁体字符串，定位是哪个模组。"""
import base64
import io
import json
import re
import zipfile

raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

KEY = re.compile(r"飽食度|攝取額度|類型設定|食物背包|疲勞|創傷|醉酒")
TRAD = re.compile(r"[飽攝額類揀據選擇開關閉發聲體們個為與這那麼誰會實現點兒]")

hits = []
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
    except Exception:
        continue
    name = bj.get("name") or "?"
    for info in zz.infolist():
        if info.file_size > 3 * 1024 * 1024:
            continue
        if not re.search(r"\.(twee|js|json|json5|html)$", info.filename, re.I):
            continue
        try:
            t = zz.read(info).decode("utf-8", "replace")
        except Exception:
            continue
        if KEY.search(t):
            n = len(KEY.findall(t))
            hits.append((name, info.filename, n))
        elif len(TRAD.findall(t)) > 30:
            hits.append((name, info.filename + " (大量繁体)", len(TRAD.findall(t))))

print("命中 %d 处：" % len(hits))
for n, f, c in hits:
    print("  %-30s %-56s %d" % (n, f, c))
