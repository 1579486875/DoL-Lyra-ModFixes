# -*- coding: utf-8 -*-
"""修 MapleBirchCE 浮层按钮「拖动后弹回」。

根因：坐标系混用。
  pointerdown 用 getBoundingClientRect().left（CSS zoom 之后的值，如 288）
  pointermove 算 drag.nx = drag.l + dx（288 + 物理位移）
  然后写回 style.left（CSS zoom 之前的坐标系，实际显示 = 值 x 0.72）
  → 下一次读取又被乘 0.72 → 每拖一次缩小一次 → 视觉上是「弹回」。

修法：drag.l / drag.t 改用 parseFloat(style.left/top)，即未缩放的 CSS 坐标；
      style 里没有值时（right/bottom 定位）再用 getBoundingClientRect 反算。
"""
import base64
import io
import json
import os
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-dragfix3.apk"

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

if not target_b64:
    raise SystemExit("❌ 未找到 MapleBirchCE")

zz = zipfile.ZipFile(io.BytesIO(src_zip))
js = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")

# 定位 pointerdown 里对 drag.l / drag.t 的赋值
OLD = '''			var r = toggleBtn.getBoundingClientRect ? toggleBtn.getBoundingClientRect() : { left: 0, top: 0, width: 56, height: 56 };
			drag.l = r.left; drag.t = r.top;
			drag.bw = r.width || 56; drag.bh = r.height || 56;'''

NEW = '''			var r = toggleBtn.getBoundingClientRect ? toggleBtn.getBoundingClientRect() : { left: 0, top: 0, width: 56, height: 56 };
			/* v2.0.13 坐标系修正：style.left/top 是「缩放前」的 CSS 坐标，
			   而 getBoundingClientRect 返回「缩放到 72% 之后」的坐标。
			   原来用后者当作拖动基准，写回 style 后实际显示被再乘一次 zoom，
			   于是每拖一次位置就缩小一次 —— 表现为「拖完弹回」。 */
			var _zs2 = 1;
			try { _zs2 = ((window.SugarCube && SugarCube.State && SugarCube.State.variables && SugarCube.State.variables.options && SugarCube.State.variables.options.zoom) || 100) / 100; } catch (_e2) {}
			if (!(_zs2 > 0)) { _zs2 = 1; }
			var _sl = parseFloat(tgSt.left), _st = parseFloat(tgSt.top);
			if (isFinite(_sl)) { drag.l = _sl; } else { drag.l = r.left / _zs2; }
			if (isFinite(_st)) { drag.t = _st; } else { drag.t = r.top / _zs2; }
			/* 宽高同样要换成未缩放值，否则钳位会偏 */
			drag.bw = (r.width || 56) / _zs2; drag.bh = (r.height || 56) / _zs2;'''

if OLD not in js:
    # 宽松匹配
    pat = re.compile(r"drag\.l = r\.left;\s*drag\.t = r\.top;\s*\n?\s*drag\.bw = r\.width \|\| 56; drag\.bh = r\.height \|\| 56;")
    if not pat.search(js):
        print("❌ 未找到赋值片段，列出附近的 drag. 赋值：")
        for mm in re.finditer(r"drag\.\w+\s*=", js):
            print("  @%d: %s" % (mm.start(), js[max(0, mm.start() - 80):mm.start() + 120].replace("\n", " ")[:200]))
        raise SystemExit(1)
    js2 = pat.sub(NEW, js, count=1)
else:
    js2 = js.replace(OLD, NEW, 1)

assert js2 != js, "未发生替换"
print("✅ 坐标系修正完成")
print("   新长度: %d -> %d" % (len(js), len(js2)))

# 重建
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

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in z.infolist():
        d = h2.encode("utf-8") if info.filename == "assets/www/index.html" else z.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

print("\n✅ 输出:", OUT, "%.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))

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
        z2 = zipfile.ZipFile(io.BytesIO(d))
        b2 = json.loads(z2.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if (b2.get("name") or "") == "MapleBirchCE":
        j2 = z2.read("javascript/maplebirchce.js").decode("utf-8", "replace")
        print("   校验 _zs2:", j2.count("_zs2"), "处")
        print("   校验 _sl/_st:", j2.count("_sl"), "/", j2.count("_st"))
        break
