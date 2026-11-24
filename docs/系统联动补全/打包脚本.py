# -*- coding: utf-8 -*-
"""重新打包联动模组：先删旧的，再加新的。"""
import base64
import io
import json
import os
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SRC = r"E:\TAML\_dol\work\联动模组"
MOD_NAME = "系统联动补全"


def build_zip(mod_dir):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for root, dirs, files in os.walk(mod_dir):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, mod_dir).replace("\\", "/")
                zo.write(full, rel)
    return buf.getvalue()


raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
body = m.group(1)

# 1) 找出旧模组的 base64 并删除
old_b64 = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', body):
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
    if (bj.get("name") or "") == MOD_NAME:
        old_b64 = s
        break

if old_b64:
    print("找到旧版本，删除")
    body = body.replace('"' + old_b64 + '"', '', 1)
    # 清理可能留下的双逗号
    body = re.sub(r",\s*,", ",", body)
    body = body.strip().rstrip(",")

# 2) 打包新版本
mod_dir = os.path.join(SRC, MOD_NAME)
data = build_zip(mod_dir)
zz = zipfile.ZipFile(io.BytesIO(data))
bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
print("新版本: %s %s  %d 字节" % (bj["name"], bj["version"], len(data)))
print("文件:", zz.namelist())

b64 = base64.b64encode(data).decode("ascii")

# 3) 追加
if body.strip():
    body = body.rstrip().rstrip(",") + ',\n"' + b64 + '"'
else:
    body = '"' + b64 + '"'

raw2 = raw[:m.start(1)] + body + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化，中止")
    sys.exit(1)

# 4) 校验 JSON
import subprocess
js = "var a = [" + body.replace("\n", "") + "]; console.log(a.length);"
open(r"E:\TAML\_dol\work\_chk.js", "w", encoding="utf-8").write(js)
r = subprocess.run(["node", r"E:\TAML\_dol\work\_chk.js"], capture_output=True, text=True, encoding="utf-8")
print("数组条目:", r.stdout.strip() or r.stderr.strip()[:200])

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
