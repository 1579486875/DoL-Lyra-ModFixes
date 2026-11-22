# -*- coding: utf-8 -*-
"""把翻译后的 Remy Love 加入 index（替换 actions-text.twee 后再插入）。"""
import base64
import io
import json
import os
import re
import sys
import zipfile

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")
SRC = r"E:\TAML\_dol\mods4\Remy.Love.Mod.mod.zip"
NEW_TWEE = os.path.join(WORK, "_remy_actions_text_zh.twee")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

# 1) 用译文重建 ZIP
new_twee = open(NEW_TWEE, encoding="utf-8").read()
zz = zipfile.ZipFile(SRC)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "game/base-combat/actions-text.twee":
            d = new_twee.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_zip = buf.getvalue()
b64 = base64.b64encode(new_zip).decode("ascii")
print("新 ZIP:", len(new_zip), "bytes")

# 2) 插入 index
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
if b64 in block:
    print("已存在，跳过插入")
else:
    block = block.rstrip()
    if not block.endswith(","):
        block += ","
    block += '\n"' + b64 + '"'
    raw = raw[:m.start(1)] + block + raw[m.end(1):]
    print("已插入")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw.encode("utf-8"))
print("✅ 写入")
