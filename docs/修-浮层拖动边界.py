# -*- coding: utf-8 -*-
"""修复 maplebirchce.js 浮层按钮拖动边界：让钳位考虑 CSS zoom。

根因：
  游戏用 $("body").css("zoom", value + "%") 缩放；
  CSS zoom 下 window.innerWidth 返回【未缩放】视口宽度，
  而元素实际可用宽度是 innerWidth / zoomScale（因为 body 被缩小了，逻辑空间变大）。
  钳位用 innerWidth 会把可拖动范围锁死在左侧，右侧拖不到。

修法：钳位前把 w/h 除以 zoomScale。

改动点（共 3 处，都在钳位逻辑里）：
  1) tgClampPos 内部
  2) pointermove 的 raf 回调
  3) pointerup 的最终钳位
"""
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-dragfix.apk"

z = zipfile.ZipFile(APK)

# 找到 MapleBirchCE 的块
import base64
import io
import json

h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

target_b64 = None
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
        target_b64 = s
        src_zip = d
        print("找到 MapleBirchCE")
        break

if not target_b64:
    raise SystemExit("❌ 未找到 MapleBirchCE")

# 读 maplebirchce.js
zz = zipfile.ZipFile(io.BytesIO(src_zip))
js = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
print("原 js:", len(js), "字节")

# 待替换片段
OLD1 = '''var w = (typeof window !== "undefined" && window.innerWidth) || 1280;
				var h = (typeof window !== "undefined" && window.innerHeight) || 720;'''

NEW1 = '''var _zs = 1; try { _zs = ((window.SugarCube && SugarCube.State && SugarCube.State.variables && SugarCube.State.variables.options && SugarCube.State.variables.options.zoom) || 100) / 100; } catch (_e) {} if (!(_zs > 0)) { _zs = 1; }
				var w = (((typeof window !== "undefined" && window.innerWidth) || 1280) / _zs);
				var h = (((typeof window !== "undefined" && window.innerHeight) || 720) / _zs);'''

cnt = js.count(OLD1)
print("待替换片段出现次数:", cnt)

if cnt == 0:
    # 尝试宽松匹配（缩进可能不同）
    pat = re.compile(
        r'var w = \(typeof window !== "undefined" && window\.innerWidth\) \|\| 1280;\s*\n\s*var h = \(typeof window !== "undefined" && window\.innerHeight\) \|\| 720;'
    )
    hits = pat.findall(js)
    print("宽松匹配:", len(hits))
    if not hits:
        raise SystemExit("❌ 未找到钳位代码")
    js2 = pat.sub(NEW1, js)
else:
    js2 = js.replace(OLD1, NEW1)

assert js2 != js, "未发生替换"
print("✅ 替换完成，新长度:", len(js2))

# 重建该模组 ZIP
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        data = js2.encode("utf-8") if info.filename == "javascript/maplebirchce.js" else zz.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)
new_zip = buf.getvalue()
print("新模组 ZIP:", len(new_zip), "字节")

# 替换进 index
new_b64 = base64.b64encode(new_zip).decode("ascii")
h2 = h.replace(target_b64, new_b64, 1)
assert h2 != h, "index 未替换"

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        d = h2.encode("utf-8") if info.filename == "assets/www/index.html" else z.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

print("\n✅ 输出:", OUT)
