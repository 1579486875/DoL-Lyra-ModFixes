# -*- coding: utf-8 -*-
"""回滚 name 为英文（靠 TRAIT_ZH 映射显示中文），保留 text 的中文翻译。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SRC = r"E:\TAML\_dol\mods\MapleBirchCE-2.1.12.mod.zip"
PREFIX = "var VANILLA_TRAITS_RAW = "
DRY = "--write" not in sys.argv

# 1) 从原始模组取英文 name 列表（按顺序）
zz_src = zipfile.ZipFile(SRC)
t_src = zz_src.read("javascript/maplebirchce.js").decode("utf-8", "replace")
i0 = t_src.find(PREFIX + "[")
j0 = t_src.find("\n];", i0)
arr_src = json.loads(re.sub(r",\s*\]\s*$", "]", t_src[i0 + len(PREFIX):j0 + 2].rstrip()))
print("原始条目:", len(arr_src))

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

target = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
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
    if (bj.get("name") or "") == "MapleBirchCE":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到")
    sys.exit(1)

s_old, zz, bj = target
t = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
i = t.find(PREFIX + "[")
j = t.find("\n];", i)
arr = json.loads(re.sub(r",\s*\]\s*$", "]", t[i + len(PREFIX):j + 2].rstrip()))
print("当前条目:", len(arr))

if len(arr) != len(arr_src):
    print("❌ 条目数不一致，中止")
    sys.exit(1)

# 2) 逐条把 name 换回英文（按索引对应，因为顺序未变）
restored = 0
for k in range(len(arr)):
    cn_name = arr[k].get("name")
    en_name = arr_src[k].get("name")
    if cn_name != en_name:
        arr[k]["name"] = en_name
        restored += 1

print("恢复 name:", restored, "条")

# 3) 保持 text（中文）

if DRY:
    print("[dry-run]")
    # 抽查
    for k in (0, 70, 150):
        print("  [%d] name=%s | text=%s" % (k, arr[k].get("name"), str(arr[k].get("text"))[:40]))
    sys.exit(0)

lines = [json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in arr]
new_arr = "[\n    " + ",\n  ".join(lines) + "\n]"
chk = json.loads(new_arr)
assert len(chk) == len(arr)
print("回读校验: %d 条 ✓" % len(chk))

# 4) 校验 name 与原始完全一致
for k in range(len(arr)):
    if arr[k].get("name") != arr_src[k].get("name"):
        print("❌ 索引 %d 的 name 不一致" % k)
        sys.exit(1)
print("name 与原始完全一致 ✓")

t2 = t[:i + len(PREFIX)] + new_arr + t[j + 2:]
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "javascript/maplebirchce.js":
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
