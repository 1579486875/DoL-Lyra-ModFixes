# -*- coding: utf-8 -*-
"""ADD_MODS：把下载的 8 个模组追加进 index 的 modDataValueZipList（备份后操作）。"""
import base64
import json
import os
import re
import shutil
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
BAK = HTML + ".bak_before_addons"
DL = r"E:\TAML\_dol\work\_downloads"

FILES = [
    "DoL-timemulti-5.4.6.1.zip",
    "DoL-kitchenplus-5.3.7.2.zip",
    "HonestMarkets-v0.5.17.0.zip",
    "More-Useful-Foodstuff-v0.2.60.mod.zip",
    "LitterPC-1.5.0-DolMod.zip",
    "1_Cattery-1.1.9-fixed-icons.1.zip",
    "revelation-the-book-of-return-v1.4.6.modpack",
    "WhitneyExpansion.zip",
]

if not os.path.exists(BAK):
    shutil.copy2(HTML, BAK)
    print("已备份 index ->", BAK)

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
if not m:
    print("❌ 找不到 modDataValueZipList")
    sys.exit(1)

# 收集新模组
new_items = []
for fn in FILES:
    p = os.path.join(DL, fn)
    data = open(p, "rb").read()
    if fn.endswith(".zip"):
        z = zipfile.ZipFile(p)
        if z.testzip() is not None:
            print("❌ ZIP 损坏:", fn)
            sys.exit(1)
        bj = json.loads(z.read("boot.json").decode("utf-8-sig")) if "boot.json" in z.namelist() else {}
        nm = bj.get("name", fn)
    else:
        nm = fn
    new_items.append((nm, base64.b64encode(data).decode("ascii")))
    print("  + %-32s %8d" % (nm, len(data)))

# 幂等：已存在同名 base64 前缀就跳过
block = m.group(1)
added = 0
for nm, b64 in new_items:
    if b64[:80] in block:
        print("  skip(已存在):", nm)
        continue
    block = block.rstrip()
    if not block.endswith(","):
        block += ","
    block += '\n"' + b64 + '"'
    added += 1

raw2 = raw[:m.start(1)] + block + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数 ->", cnt2, "| 新增", added)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入", HTML, len(raw2))
