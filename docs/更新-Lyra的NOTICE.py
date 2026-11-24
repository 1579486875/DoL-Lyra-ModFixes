# -*- coding: utf-8 -*-
"""用最新模板覆盖 Lyra 模组的 NOTICE.md（幂等，可重复执行）。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SCRIPT = r"E:\TAML\_dol\work\加-整合包声明.py"

# 从脚本里提取 NOTICE 模板（NOTICE = """..."""）
src = open(SCRIPT, encoding="utf-8").read()
m = re.search(r'NOTICE\s*=\s*"""(.*?)"""', src, re.S)
if not m:
    print("❌ 脚本里找不到 NOTICE 模板")
    sys.exit(1)
NOTICE = m.group(1)
print("NOTICE 模板长度:", len(NOTICE))

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
mm = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

target = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mm.group(1)):
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
    if (bj.get("name") or "") == "Lyra":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到 Lyra")
    sys.exit(1)

s_old, zz, bj = target
print("现有文件:", zz.namelist())

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    written = set()
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "NOTICE.md":
            d = NOTICE.encode("utf-8")
            written.add("NOTICE.md")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
    if "NOTICE.md" not in written:
        zo.writestr("NOTICE.md", NOTICE.encode("utf-8"))

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)

m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
n_b = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', mm.group(1)))
n_a = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
if n_b != n_a:
    print("❌ 条目数变化", n_b, n_a)
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ NOTICE.md 已更新（%d 字节）" % len(NOTICE.encode("utf-8")))
