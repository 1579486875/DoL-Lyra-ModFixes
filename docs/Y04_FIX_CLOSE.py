# -*- coding: utf-8 -*-
"""修 exportOutfit 的 _fallback 关闭逻辑：捕获阶段 + touchend + 定时兜底。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

OLD = '''			const close = function () {
				try { ta.remove(); hint.remove(); } catch (e) {}
				document.removeEventListener("click", close);
			};
			window.setTimeout(function () { document.addEventListener("click", close); }, 300);'''

NEW = '''			let _closed = false;
			const close = function (ev) {
				if (_closed) return;
				/* 点在文本区域内时不关闭，允许选中/长按复制 */
				try {
					if (ev && (ev.target === ta || (ta.contains && ta.contains(ev.target)))) return;
				} catch (e0) {}
				_closed = true;
				try { ta.remove(); } catch (e1) {}
				try { hint.remove(); } catch (e2) {}
				try {
					document.removeEventListener("click", close, true);
					document.removeEventListener("touchend", close, true);
					document.removeEventListener("mousedown", close, true);
				} catch (e3) {}
			};
			window.setTimeout(function () {
				try {
					document.addEventListener("click", close, true);
					document.addEventListener("touchend", close, true);
					document.addEventListener("mousedown", close, true);
				} catch (e4) {}
			}, 300);
			/* 兜底：15 秒后无论如何都收掉，避免残留挡住界面 */
			window.setTimeout(function () {
				try { if (!_closed) { _closed = true; ta.remove(); hint.remove(); } } catch (e5) {}
			}, 15000);'''

if OLD not in raw:
    print("❌ 锚点未找到")
    sys.exit(1)

raw2 = raw.replace(OLD, NEW, 1)
print("已替换 _fallback 关闭逻辑")

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
