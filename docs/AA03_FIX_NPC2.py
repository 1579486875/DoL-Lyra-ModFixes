# -*- coding: utf-8 -*-
"""用正则把 NPC.Avatars 的英文分支去掉（忽略空白差异）。"""
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
    if "NPC Avatars" in (bj.get("name") or ""):
        target = (s, zz, bj)
        break

if not target:
    sys.exit(1)
s_old, zz, bj = target
t = zz.read("game/base-system/ovelays/bsa-check.twee").decode("utf-8", "replace")

# 策略：把每个 <<if window.modUtils.getMod('ModI18N')>> ... <<else>> ... <</if>> 整块
# 替换成「只保留 if 分支」
pat = re.compile(
    r"<<if\s+window\.modUtils\.getMod\('ModI18N'\)>>(.*?)<<else>>(.*?)<</if>>",
    re.S)

def fix(mm):
    keep = mm.group(1)
    return keep

t2, n = pat.subn(fix, t)
print("替换块数:", n)
print("改后长度:", len(t), "->", len(t2))
print("剩余英文关键词:", "Why are there no images" in t2, "Image Instructions" in t2)

if n == 0:
    # 打印实际文本看结构
    i = t.find("ModI18N")
    print("实际片段:", repr(t[max(0, i - 200):i + 600]))
    sys.exit(1)

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "game/base-system/ovelays/bsa-check.twee":
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
