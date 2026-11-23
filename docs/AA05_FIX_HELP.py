# -*- coding: utf-8 -*-
"""把 more useful foodstuff 的 outsideHelp 改为捕获阶段监听，并同步 cleanup。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

target = None
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
    if "foodstuff" in (bj.get("name") or "").lower() or "食物" in (bj.get("name") or ""):
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到")
    sys.exit(1)

s_old, zz, bj = target
print("命中:", bj.get("name"))
t = zz.read("food-effects.js").decode("utf-8", "replace")

OLD_ADD = "document.addEventListener('click',outsideHelp);"
NEW_ADD = "document.addEventListener('click',outsideHelp,true);"
OLD_REM = "document.removeEventListener('click',outsideHelp);"
NEW_REM = "document.removeEventListener('click',outsideHelp,true);"

c1 = t.count(OLD_ADD)
c2 = t.count(OLD_REM)
print("add 匹配:", c1, "| remove 匹配:", c2)

if c1 == 0:
    print("❌ add 未匹配")
    i = t.find("outsideHelp")
    print(repr(t[max(0, i - 100):i + 500]))
    sys.exit(1)

t2 = t.replace(OLD_ADD, NEW_ADD).replace(OLD_REM, NEW_REM)

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "food-effects.js":
            d = t2.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
