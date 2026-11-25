# -*- coding: utf-8 -*-
"""正确验证：解码模组 base64，检查 prop 补丁是否在。"""
import base64
import io
import json
import re
import zipfile

S = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(S, "rb").read().decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
ents = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1))
print("模组条目:", len(ents))

for s in ents:
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
    if nm != "系统联动补全":
        continue
    t = zz.read("scripts/core.js").decode("utf-8", "replace")
    print("\n=== 系统联动补全 core.js ===")
    print("  长度:", len(t))
    for k in ("PHONE_SHOP_PATCH", "TOILET_PATCH", "YENOTE_TEXT_PATCH", "NPC_TITLE_FIX", "PROP_FOLDER_FIX", "propFolderFix"):
        print("  %-20s %s" % (k, "✅" if k in t else "❌"))
    break
