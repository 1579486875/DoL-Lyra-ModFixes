# -*- coding: utf-8 -*-
"""修正食物桥接：用 State.variables.BasicNeeds 而不是 window.BN。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")

# 找 More-Useful-Foodstuff 的当前 base64
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
target_b64 = None
for s in parts:
    try:
        data = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if data[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(data))
        if "food-effects.js" in zz.namelist():
            target_b64 = s
            break
    except Exception:
        continue
if not target_b64:
    print("❌ 没找到 food-effects.js 模组")
    sys.exit(1)

data = base64.b64decode(re.sub(r"\s+", "", target_b64))
zz = zipfile.ZipFile(io.BytesIO(data))
js = zz.read("food-effects.js").decode("utf-8", "replace")

OLD = ('const _bn = window.BN && window.BN.ensureVars ? window.BN.ensureVars() : null;')
NEW = ('const _bn = (window.SugarCube && SugarCube.State && SugarCube.State.variables) ? SugarCube.State.variables.BasicNeeds : null;')
if OLD not in js:
    print("⚠ 找不到旧桥接行")
    sys.exit(1)
js2 = js.replace(OLD, NEW, 1)
js2 = js2.replace("if (window.BN.updatePanel) window.BN.updatePanel();", "")
print("桥接行已替换")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "food-effects.js":
            d = js2.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_data = buf.getvalue()
new_b64 = base64.b64encode(new_data).decode("ascii")

raw2 = raw.replace(target_b64, new_b64, 1)
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写回 index")
