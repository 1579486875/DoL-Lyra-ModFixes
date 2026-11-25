# -*- coding: utf-8 -*-
"""完整修复 MapleBirchCE 浮层按钮拖动：钳位 + 坐标系。

背景：第43轮的 _zs 钳位修改丢失（当时未部署，后续以 out 为底重打包把它冲掉了），
      这次一次做全，并修正「拖动弹回」的坐标系问题。

两处修改：
A) 钳位：window.innerWidth/Height 在 CSS zoom 下是未缩放视口宽度，
   元素实际可用空间是 innerWidth / zoomScale，所以要除。
B) 坐标系：drag.l/t 应该用 style.left/top（未缩放的 CSS 坐标），
   不能用 getBoundingClientRect()（已缩放），否则每拖一次位置被乘一次 zoom → 弹回。
"""
import base64
import io
import json
import os
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
OUT = r"E:\TAML\_dol\work\DoL-dragfix-full.apk"

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
print("原始长度:", len(js))

# ============ A) 钳位：把 window.innerWidth/Height 除以 zoomScale ============
ZS_DECL = '''/* v2.0.13 zoom 修正：CSS zoom 下 innerWidth 是未缩放值，
   元素可用空间是 innerWidth/zoomScale，钳位必须除。 */
		function _mbceZoomScale() {
			var z2 = 1;
			try { z2 = ((window.SugarCube && SugarCube.State && SugarCube.State.variables && SugarCube.State.variables.options && SugarCube.State.variables.options.zoom) || 100) / 100; } catch (_e) {}
			if (!(z2 > 0)) { z2 = 1; }
			return z2;
		}
'''

pat_clamp = re.compile(
    r'var w = \(typeof window !== "undefined" && window\.innerWidth\) \|\| 1280;\s*'
    r'(?:/\*[^*]*\*/\s*)?'
    r'var h = \(typeof window !== "undefined" && window\.innerHeight\) \|\| 720;'
)
cnt_clamp = len(pat_clamp.findall(js))
print("钳位片段数:", cnt_clamp)

NEW_CLAMP = '''var _zsv = _mbceZoomScale();
				var w = (((typeof window !== "undefined" && window.innerWidth) || 1280) / _zsv);
				var h = (((typeof window !== "undefined" && window.innerHeight) || 720) / _zsv);'''

if cnt_clamp == 0:
    print("⚠ 未找到钳位片段，列出所有 innerWidth 用法：")
    for mm in re.finditer(r"window\.innerWidth", js):
        print("  @%d: %s" % (mm.start(), js[max(0, mm.start() - 100):mm.start() + 150].replace("\n", " ")[:240]))
    raise SystemExit(1)

js2 = pat_clamp.sub(NEW_CLAMP, js)
print("✅ A) 钳位已改 %d 处" % cnt_clamp)

# 插入 _mbceZoomScale 声明（放在第一个 tgClampPos 之前）
anchor = "function tgClampPos() {"
if anchor not in js2:
    # 找其他的锚点
    m = re.search(r"var tgSt = toggleBtn\.style \|\| \{\};", js2)
    if m:
        js2 = js2[:m.end()] + "\n\t\t" + ZS_DECL + js2[m.end():]
        print("✅ A) _mbceZoomScale 已插入（tgSt 后）")
    else:
        raise SystemExit("❌ 找不到插入点")
else:
    i = js2.index(anchor)
    js2 = js2[:i] + ZS_DECL + "\t\t" + js2[i:]
    print("✅ A) _mbceZoomScale 已插入（tgClampPos 前）")

# ============ B) 坐标系：drag.l/t 用 style 而非 getBoundingClientRect ============
OLD_B = '''			var r = toggleBtn.getBoundingClientRect ? toggleBtn.getBoundingClientRect() : { left: 0, top: 0, width: 56, height: 56 };
			drag.l = r.left; drag.t = r.top;
			drag.bw = r.width || 56; drag.bh = r.height || 56;'''

NEW_B = '''			var r = toggleBtn.getBoundingClientRect ? toggleBtn.getBoundingClientRect() : { left: 0, top: 0, width: 56, height: 56 };
			/* 坐标系修正：style.left/top 是缩放前的 CSS 坐标，
			   getBoundingClientRect 返回缩放后的坐标。用后者当拖动基准，
			   写回 style 后又被乘一次 zoom，于是每拖一次缩小一次 —— 表现为「弹回」。 */
			var _zsv2 = _mbceZoomScale();
			var _sl = parseFloat(tgSt.left), _st = parseFloat(tgSt.top);
			drag.l = isFinite(_sl) ? _sl : (r.left / _zsv2);
			drag.t = isFinite(_st) ? _st : (r.top / _zsv2);
			drag.bw = (r.width || 56) / _zsv2;
			drag.bh = (r.height || 56) / _zsv2;'''

pat_b = re.compile(r"drag\.l = r\.left;\s*drag\.t = r\.top;\s*\n?\s*drag\.bw = r\.width \|\| 56; drag\.bh = r\.height \|\| 56;")
if pat_b.search(js2):
    js2 = pat_b.sub(NEW_B, js2, count=1)
    print("✅ B) 坐标系已改（宽松匹配）")
elif OLD_B in js2:
    js2 = js2.replace(OLD_B, NEW_B, 1)
    print("✅ B) 坐标系已改（精确匹配）")
else:
    print("⚠ B) 未找到坐标系片段，跳过")

assert js2 != js
print("\n最终长度: %d -> %d" % (len(js), len(js2)))

# 校验
print("\n=== 校验 ===")
print("  _mbceZoomScale:", js2.count("_mbceZoomScale"), "处")
print("  _zsv:", js2.count("_zsv"), "处")
print("  残留裸 innerWidth 钳位:", len(re.findall(r'window\.innerWidth\) \|\| 1280;', js2)))
print("  残留 drag.l = r.left:", len(re.findall(r"drag\.l = r\.left;", js2)))

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
