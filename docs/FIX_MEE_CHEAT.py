# -*- coding: utf-8 -*-
"""给 MapleBirchCE 的「模组作弊」加露出拓展适配器（欲望 / 满足）。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

# 找 MapleBirchCE
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
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
        if "boot.json" not in zz.namelist():
            continue
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        if bj.get("name") == "MapleBirchCE":
            target = (s, zz, bj)
            break
    except Exception:
        continue
if not target:
    print("❌ 没找到 MapleBirchCE")
    sys.exit(1)
s_old, zz, bj = target
print("命中:", bj.get("name"), bj.get("version"))

JS = "javascript/maplebirchce.js"
js = zz.read(JS).decode("utf-8", "replace")

ADAPTER = '''
	/* [DoL-Lyra] 露出拓展（MyExhibitionismExpansion）适配器：欲望 / 满足
	   这两个是模组私有变量（V.desire / V.satisfaction，0-1000），
	   「勇气」「镇静」是由它们派生的值，不单独暴露（改派生值没有存储位置）。 */
	CHEAT_ADAPTERS["my-exhibitionism-expansion"] = {
		detect: function () {
			try {
				return typeof window.mee === "object" && !!window.mee && typeof window.mee.setDesire === "function";
			} catch (e) { return false; }
		},
		entry: {
			modId: "my-exhibitionism-expansion",
			modName: "露出拓展 v1.0.4",
			tasks: [],
			stages: [],
			abilities: [],
			scenes: [],
			values: [
				{ key: "mee_desire", name: "欲望", varPath: "desire", type: "number", min: 0, max: 1000,
				  note: "0-1000，默认 500。越高：勇气↑、镇静↓；每分钟自然 -0.1。" },
				{ key: "mee_satisfaction", name: "满足", varPath: "satisfaction", type: "number", min: 0, max: 1000,
				  note: "0-1000，默认 300。勇气/镇静的基础值，满足高则两者都高。" }
			],
			actions: []
		}
	};
'''

ANCHOR = "var CHEAT_ADAPTERS = {};"
if ANCHOR not in js:
    print("❌ 找不到 CHEAT_ADAPTERS 定义")
    sys.exit(1)
if 'CHEAT_ADAPTERS["my-exhibitionism-expansion"]' in js:
    print("已存在适配器，跳过")
    sys.exit(0)
js2 = js.replace(ANCHOR, ANCHOR + ADAPTER, 1)
print("插入适配器:", len(js), "->", len(js2))

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == JS:
            d = js2.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt2 = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 模组数:", cnt2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
