# -*- coding: utf-8 -*-
"""FIX-R7B：修 LocationsExt 补丁里的 <<br>> -> <br>（改 index 内嵌的模组 ZIP）。

现象：Harvest Street 报 macro <<br>> does not exist
根因：LocationsExt_v1.8.1 的 boot.json 里
      replace = "<<br>><<roadicon>><<link [[快速旅行（乡间道路）|Farm Fast Travel]]>><</link>><br><<set $eventskip to 0>>"
      开头多了一个 '<'（应为 <br>），TweeReplacer 把它注入 passage 后触发宏错误。
修法：只改这一个字符串，重新打包该模组 ZIP，再写回 index 的 modDataValueZipList。
"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass != 16088:
    print("❌ passage 数异常", npass)
    sys.exit(1)

# 1) 定位 modDataValueZipList
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
if not m:
    print("❌ 找不到 modDataValueZipList")
    sys.exit(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
print("模组 ZIP 条目:", len(parts))

target = None
for s in parts:
    try:
        data = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if data[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(data))
    except Exception:
        continue
    names = zz.namelist()
    if "boot.json" not in names:
        continue
    try:
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    blob = json.dumps(bj, ensure_ascii=False)
    if "LocationsExt" in blob or "乡间道路" in blob:
        target = (s, data, zz, bj)
        print("✅ 命中 LocationsExt：", bj.get("name"), bj.get("version"))
        break

if not target:
    print("❌ 没找到 LocationsExt 模组")
    sys.exit(1)

s_old, data, zz, bj = target
boot_txt = zz.read("boot.json").decode("utf-8-sig")
before = boot_txt.count("\\u003c\\u003cbr\\u003e\\u003e") + boot_txt.count("<<br>>")
print("boot.json 里 <<br>> 变体:", before)

if before == 0:
    print("✓ 无需修改")
    sys.exit(0)

# 2) 只改这一处：<<br>> / \u003c\u003cbr\u003e\u003e -> <br>
nb = boot_txt.replace("\\u003c\\u003cbr\\u003e\\u003e", "\\u003cbr\\u003e").replace("<<br>>", "<br>")
# 校验 JSON 仍可解析
json.loads(nb)
print("改后剩余:", nb.count("\\u003c\\u003cbr\\u003e\\u003e") + nb.count("<<br>>"))

# 3) 重新打包该模组 ZIP
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "boot.json":
            d = nb.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_data = buf.getvalue()
print("新 ZIP 大小:", len(new_data), "旧:", len(data))

# 4) 写回 base64
nb64 = base64.b64encode(new_data).decode("ascii")
pat = re.compile(r'"' + re.escape(s_old[:80]) + r'[A-Za-z0-9+/=\s]*"')
new_block, cnt = pat.subn(lambda _: '"' + nb64 + '"', block, count=1)
if cnt != 1:
    print("❌ base64 替换失败", cnt)
    sys.exit(1)

raw2 = raw[:m.start(1)] + new_block + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
if npass2 != npass:
    print("❌ passage 数变化", npass, "->", npass2)
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 已写回 index，passage =", npass2)
