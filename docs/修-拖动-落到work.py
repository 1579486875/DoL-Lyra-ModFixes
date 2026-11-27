# -*- coding: utf-8 -*-
r"""把 MapleBirchCE 拖动修复应用到 work\index_modded6.html（打包权威源）。

历史教训：
  第 43 轮修了 _zs 钳位 -> 只改 out 的 APK，未落地 work -> 第 48 轮被重打包冲掉
  第 50 轮修了坐标系+钳位 -> 同样只改 out -> 第 51 轮又被 work 覆盖，用户报「拖动限制又回来了」

结论：任何对 index 的修改必须写进 work\index_modded6.html，out 只是产物。
"""
import base64
import io
import json
import re
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"

h = open(HTML, encoding="utf-8", errors="replace").read()
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)
body = mz.group(1)

target_b64 = None
src_zip = None
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
    if (bj.get("name") or "") == "MapleBirchCE":
        target_b64, src_zip = s, d
        break

if not target_b64:
    raise SystemExit("❌ 未找到 MapleBirchCE")

zz = zipfile.ZipFile(io.BytesIO(src_zip))
js = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
print("原始长度:", len(js), "字符")

if "_mbceZoomScale" in js:
    print("⚠ 已有修复，跳过")
    raise SystemExit(0)

# ===== A) 插入 zoomScale 辅助函数 =====
ZS_DECL = '''/* v2.0.13 zoom 修正：CSS zoom 下 innerWidth 是未缩放值，
   元素可用空间是 innerWidth/zoomScale，钳位必须除。 */
		function _mbceZoomScale() {
			var z2 = 1;
			try { z2 = ((window.SugarCube && SugarCube.State && SugarCube.State.variables && SugarCube.State.variables.options && SugarCube.State.variables.options.zoom) || 100) / 100; } catch (_e) {}
			if (!(z2 > 0)) { z2 = 1; }
			return z2;
		}
'''

anchor = "function tgClampPos() {"
if anchor not in js:
    m = re.search(r"var tgSt = toggleBtn\.style \|\| \{\};", js)
    if not m:
        raise SystemExit("❌ 找不到插入点")
    js2 = js[:m.end()] + "\n\t\t" + ZS_DECL + js[m.end():]
else:
    i = js.index(anchor)
    js2 = js[:i] + ZS_DECL + "\t\t" + js[i:]

# ===== B) 钳位：innerWidth/Height 除以 zoomScale =====
pat_clamp = re.compile(
    r'var w = \(typeof window !== "undefined" && window\.innerWidth\) \|\| 1280;\s*'
    r'(?:/\*[^*]*\*/\s*)?'
    r'var h = \(typeof window !== "undefined" && window\.innerHeight\) \|\| 720;'
)
cnt = len(pat_clamp.findall(js2))
NEW_CLAMP = '''var _zsv = _mbceZoomScale();
				var w = (((typeof window !== "undefined" && window.innerWidth) || 1280) / _zsv);
				var h = (((typeof window !== "undefined" && window.innerHeight) || 720) / _zsv);'''
if cnt == 0:
    raise SystemExit("❌ 未找到钳位片段")
js2 = pat_clamp.sub(NEW_CLAMP, js2)
print("✅ A) 钳位已改 %d 处" % cnt)

# ===== C) 坐标系：drag.l/t 用 style 而非 getBoundingClientRect =====
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
    print("✅ B) 坐标系已改")
else:
    raise SystemExit("❌ 未找到坐标系片段")

# ===== 重建模组 ZIP，写回 index =====
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

open(HTML, "w", encoding="utf-8").write(h2)

print("\n最终长度: %d -> %d 字符" % (len(js), len(js2)))
print("=== 校验 ===")
print("  _mbceZoomScale:", js2.count("_mbceZoomScale"))
print("  _zsv:", js2.count("_zsv"))
print("  残留裸 innerWidth 钳位:", len(re.findall(r'window\.innerWidth\) \|\| 1280;', js2)))
print("  残留 drag.l = r.left:", len(re.findall(r"drag\.l = r\.left;", js2)))
print("\n✅ 已写回", HTML)
