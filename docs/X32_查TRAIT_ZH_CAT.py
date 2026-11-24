# -*- coding: utf-8 -*-
"""查 TRAIT_ZH_CAT 的用法：是用 name 做 key 吗？"""
import base64
import io
import json
import re
import zipfile

raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
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
    if (bj.get("name") or "") != "MapleBirchCE":
        continue
    t = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")

    # 找 TRAIT_ZH_CAT 定义与用法
    print("=== TRAIT_ZH_CAT 定义位置 ===")
    for mm in list(re.finditer(r"TRAIT_ZH_CAT\s*=", t))[:2]:
        print("  @%d: %s" % (mm.start(), repr(t[mm.start():mm.start() + 400]))[:500])
        print()

    print("=== TRAIT_ZH_CAT 的引用 ===")
    for mm in list(re.finditer(r"TRAIT_ZH_CAT", t)):
        if "TRAIT_ZH_CAT\s*=" in t[mm.start():mm.start() + 20]:
            continue
        seg = t[max(0, mm.start() - 200):mm.start() + 250]
        print("  @%d: %s" % (mm.start(), repr(seg).replace("\\n", " ")[:400]))
        print()

    print("=== TRAIT_ZH_ 其它映射 ===")
    for mm in re.finditer(r"var (TRAIT_\w+)\s*=", t):
        print("  ", mm.group(1))
    break
