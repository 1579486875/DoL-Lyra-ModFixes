# -*- coding: utf-8 -*-
"""验证 index_modded6.html 里「系统联动补全」模组的实际内容。"""
import base64
import io
import json
import re
import zipfile

h = open(r"E:\TAML\_dol\work\index_modded6.html", encoding="utf-8").read()
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

print("=== 遍历所有模组 ===")
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
    if nm != "系统联动补全":
        continue
    print("\n【%s】v%s" % (nm, bj.get("version")))
    print("  文件:", zz.namelist())
    core = zz.read("scripts/core.js").decode("utf-8", "replace")
    print("  core.js: %d 字节" % len(core))
    print("  === 关键补丁检查 ===")
    for k in ("CHEAT_FACE_FIX_V2", "ARTICLE_FIX", "articleFix", "POSSESSIVE_FIX",
              "PROP_FOLDER_FIX", "inOwnHome 修正版", "PHONE_SHOP_PATCH", "TOILET_PATCH",
              "YENOTE_TEXT_PATCH", "NPC_TITLE_FIX"):
        print("    %-24s %s" % (k, "✅" if k in core else "❌"))
    break
else:
    print("❌ 没找到「系统联动补全」")
