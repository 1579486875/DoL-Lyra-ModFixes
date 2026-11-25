# -*- coding: utf-8 -*-
"""直接修 BasicNeeds 的 Ban-household.js：
1) 拦截洗澡链接时记录 a.dataset.passage 到 bnBathTarget
2) 兜底时用 bnBathTarget 而不是硬编码 'Bath'
"""
import base64
import io
import json
import os
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-bathfix.apk"

z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

target_b64 = None
src_zip = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
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
    if (bj.get("name") or "") == "BasicNeeds":
        target_b64, src_zip = s, d
        break

if not target_b64:
    raise SystemExit("❌ 未找到 BasicNeeds")

zz = zipfile.ZipFile(io.BytesIO(src_zip))
js = zz.read("scripts/Ban-household.js").decode("utf-8", "replace")
print("Ban-household.js:", len(js), "字符")

# ---------- 改动 1：声明 bnBathTarget ----------
OLD1 = "let bnBathFrom = 'Bathroom';"
NEW1 = "let bnBathFrom = 'Bathroom';\nlet bnBathTarget = null; // 本次洗澡原链接的目标 passage（兜底用，避免硬编码 'Bath' 回孤儿院）"
if OLD1 not in js:
    raise SystemExit("❌ 找不到 bnBathFrom 声明")
js2 = js.replace(OLD1, NEW1, 1)
print("✅ 1) 声明 bnBathTarget")

# ---------- 改动 2：拦截时记录目标 ----------
OLD2 = """        bnBathChoice = {};
        bnBathLinkEl = a;
        bnBathFrom = SugarCube.State.passage;"""
NEW2 = """        bnBathChoice = {};
        bnBathLinkEl = a;
        bnBathFrom = SugarCube.State.passage;
        bnBathTarget = (a.dataset && a.dataset.passage) || null;"""
if OLD2 not in js2:
    # 缩进可能不同，用宽松匹配
    pat = re.compile(r"(bnBathLinkEl = a;\s*\n\s*bnBathFrom = SugarCube\.State\.passage;)")
    if not pat.search(js2):
        raise SystemExit("❌ 找不到拦截赋值处")
    js2 = pat.sub(r"\1\n        bnBathTarget = (a.dataset && a.dataset.passage) || null;", js2, count=1)
else:
    js2 = js2.replace(OLD2, NEW2, 1)
print("✅ 2) 拦截时记录 bnBathTarget")

# ---------- 改动 3：兜底用 bnBathTarget ----------
OLD3 = """    } else {
      bnBathPending = true;
      SugarCube.Engine.play('Bath');
    }"""
NEW3 = """    } else {
      bnBathPending = true;
      // 原版此处硬编码 'Bath'（孤儿院浴室），跨地点洗澡会错误回孤儿院；
      // 改用拦截时记下的真实目标，取不到才退回 'Bath'
      SugarCube.Engine.play(bnBathTarget || 'Bath');
    }"""
cnt3 = js2.count(OLD3)
if cnt3 == 0:
    pat3 = re.compile(r"SugarCube\.Engine\.play\('Bath'\);")
    hits = pat3.findall(js2)
    print("   宽松匹配 play('Bath'):", len(hits))
    if not hits:
        raise SystemExit("❌ 找不到兜底 play('Bath')")
    js2 = pat3.sub("SugarCube.Engine.play(bnBathTarget || 'Bath');", js2)
else:
    js2 = js2.replace(OLD3, NEW3, 1)
print("✅ 3) 兜底改用 bnBathTarget")

# ---------- 校验 ----------
assert "bnBathTarget" in js2
print("\n=== 校验 ===")
print("bnBathTarget 出现:", js2.count("bnBathTarget"), "次")
print("残留裸 play('Bath'):", len(re.findall(r"Engine\.play\('Bath'\)", js2)))
print("新长度:", len(js2))

# ---------- 重建模组 ZIP ----------
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        data = js2.encode("utf-8") if info.filename == "scripts/Ban-household.js" else zz.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)
new_zip = buf.getvalue()
print("新模组 ZIP:", len(new_zip), "字节")

# ---------- 替换进 index ----------
new_b64 = base64.b64encode(new_zip).decode("ascii")
h2 = h.replace(target_b64, new_b64, 1)
assert h2 != h
open(r"E:\TAML\_dol\work\index_modded6.html", "wb").write(h2.encode("utf-8"))
print("✅ index 已更新")
