# -*- coding: utf-8 -*-
"""修 NoTraumaClamp 的 ReplacePatcher 锚点（适配当前 traumaClamp 代码），写回 index。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SRC = r"E:\TAML\_dol\work\_downloads\NoTraumaClamp_0.2.1.zip"

OLD = "if (V.trauma >= V.traumamax) V.beauty -= (V.trauma - V.traumamax) / 5;"
NEW = "V.beauty -= overflow * 0.2;"
TO_OLD = "if (V.trauma >= V.traumamax) V.beauty -= 0 ;"
TO_NEW = "V.beauty -= 0;"

z = zipfile.ZipFile(SRC)
boot = z.read("boot.json").decode("utf-8-sig")
if OLD not in boot:
    print("⚠ 旧 from 不在 boot.json")
    sys.exit(1)
nb = boot.replace(OLD, NEW).replace(TO_OLD, TO_NEW)
json.loads(nb)
print("from ->", NEW, "| to ->", TO_NEW)

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        d = z.read(info.filename)
        if info.filename == "boot.json":
            d = nb.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_zip = buf.getvalue()

old_b64 = base64.b64encode(open(SRC, "rb").read()).decode("ascii")
new_b64 = base64.b64encode(new_zip).decode("ascii")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
if old_b64 not in raw:
    print("⚠ index 里没找到 NoTraumaClamp 旧 base64")
    sys.exit(1)
raw2 = raw.replace(old_b64, new_b64, 1)
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写回 index")
