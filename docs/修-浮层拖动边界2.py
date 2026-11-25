# -*- coding: utf-8 -*-
"""补上第 3 处钳位（pointerup 的最终钳位）。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\work\DoL-dragfix.apk"
OUT = r"E:\TAML\_dol\work\DoL-dragfix2.apk"

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
    if (bj.get("name") or "") == "MapleBirchCE":
        target_b64, src_zip = s, d
        break

zz = zipfile.ZipFile(io.BytesIO(src_zip))
js = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")

# 找所有剩余的「innerWidth ... 1280」
pat = re.compile(r'var w = \(typeof window !== "undefined" && window\.innerWidth\) \|\| 1280;')
hits = [m.start() for m in pat.finditer(js)]
print("剩余待修:", len(hits))
for i in hits:
    print("  @%d 上下文: %s" % (i, js[max(0, i - 120):i + 160].replace("\n", " ")[:280]))

if not hits:
    print("✅ 已全部替换")
    raise SystemExit(0)

NEW = '''var _zs = 1; try { _zs = ((window.SugarCube && SugarCube.State && SugarCube.State.variables && SugarCube.State.variables.options && SugarCube.State.variables.options.zoom) || 100) / 100; } catch (_e) {} if (!(_zs > 0)) { _zs = 1; }
				var w = (((typeof window !== "undefined" && window.innerWidth) || 1280) / _zs);'''

js2 = pat.sub(NEW, js)

# 同时处理配对的 innerHeight
pat2 = re.compile(r'var h = \(typeof window !== "undefined" && window\.innerHeight\) \|\| 720;')
hits2 = [m.start() for m in pat2.finditer(js2)]
print("剩余 innerHeight:", len(hits2))
if hits2:
    js2 = pat2.sub('var h = (((typeof window !== "undefined" && window.innerHeight) || 720) / _zs);', js2)

print("新长度:", len(js2))

# 重建模组
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        data = js2.encode("utf-8") if info.filename == "javascript/maplebirchce.js" else zz.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)
new_zip = buf.getvalue()

new_b64 = base64.b64encode(new_zip).decode("ascii")
h2 = h.replace(target_b64, new_b64, 1)
assert h2 != h

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        d = h2.encode("utf-8") if info.filename == "assets/www/index.html" else z.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

print("\n✅ 输出:", OUT)

# 校验
z3 = zipfile.ZipFile(OUT)
h3 = z3.read("assets/www/index.html").decode("utf-8", "replace")
mz3 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h3, re.S)
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz3.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz2 = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz2.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if (bj.get("name") or "") == "MapleBirchCE":
        j2 = zz2.read("javascript/maplebirchce.js").decode("utf-8", "replace")
        print("   校验：剩余裸 innerWidth 钳位 = %d 处" % len(re.findall(r'window\.innerWidth\) \|\| 1280;', j2)))
        print("   校验：_zs 变量出现 = %d 次" % j2.count("_zs"))
        break
