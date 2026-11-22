# -*- coding: utf-8 -*-
"""修猫咖的 Containers 补丁锚点（补上 DoLSims 加的 <<handheldon>>），并写回 index。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SRC = r"E:\TAML\_dol\work\_downloads\1_Cattery-1.1.9-fixed-icons.1.zip"

OLD_FIND = '<<getouticon>><<link [[离开|_container.leaveLink]]>><</link>>'
NEW_FIND = '<<getouticon>><<link [[离开|_container.leaveLink]]>><<handheldon>><</link>>'
OLD_REP = ('<<if $pcfzjswdl is 1>>\n<<getouticon>><<link [[离开|Pc House Study]]>><<set $pcfzjswdl to 0>><</link>>\n'
           '\t<<else>>\n\t<<getouticon>><<link [[离开|_container.leaveLink]]>><</link>><</if>>')
NEW_REP = ('<<if $pcfzjswdl is 1>>\n<<getouticon>><<link [[离开|Pc House Study]]>><<set $pcfzjswdl to 0>><</link>>\n'
           '\t<<else>>\n\t<<getouticon>><<link [[离开|_container.leaveLink]]>><<handheldon>><</link>><</if>>')

z = zipfile.ZipFile(SRC)
boot = z.read("boot.json").decode("utf-8-sig")
if OLD_FIND not in boot:
    print("⚠ boot.json 里没找到旧 findString")
    sys.exit(1)
nb = boot.replace(OLD_FIND, NEW_FIND).replace(OLD_REP, NEW_REP)
json.loads(nb)

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
print("新 ZIP:", len(new_zip), "旧:", len(open(SRC, "rb").read()))

old_b64 = base64.b64encode(open(SRC, "rb").read()).decode("ascii")
new_b64 = base64.b64encode(new_zip).decode("ascii")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
if old_b64 not in raw:
    print("⚠ index 里没找到猫咖旧 base64")
    sys.exit(1)
raw2 = raw.replace(old_b64, new_b64, 1)
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 已写回 index，size", len(raw2))
