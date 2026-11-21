# -*- coding: utf-8 -*-
"""FIX-R7F：修服装套装"导出"（复制到剪贴板）在 Android WebView 下无反应。

根因：
  1) navigator.clipboard.writeText 在 WebView/非安全上下文里可能不存在 → 直接抛异常
  2) 没有 fallback
  3) element.text = "Copied!" 不是 DOM 属性（应为 textContent）

修法（②兜底，保意图）：
  - 优先 clipboard API
  - 失败/不存在时：弹出只读 textarea + execCommand("copy")，仍不行则提示长按复制
  - textContent 修正 + "已复制"提示
"""
import html as H
import re
import subprocess
import sys
import tempfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
if npass != 16088:
    print("❌ passage", npass)
    sys.exit(1)

# 旧函数（从 index 精确截取）
i = raw.find("function exportOutfit(outfitIndex) {")
if i < 0:
    print("❌ 找不到 exportOutfit")
    sys.exit(1)
j = raw.find("window.exportOutfit = exportOutfit;", i)
if j < 0:
    print("❌ 找不到函数结尾")
    sys.exit(1)
OLD = raw[i:j]
print("旧函数长度:", len(OLD))

NEW = '''function exportOutfit(outfitIndex) {
	const outfit = { ...V.outfit[outfitIndex] };

	for (const property in outfit) {
		if (["index", "location", "hairStyle"].includes(property) || outfit[property] === "naked") {
			Reflect.deleteProperty(outfit, property);
		}
	}

	if (outfit.colors) {
		for (const property in outfit.colors) {
			if (outfit.colors[property][0] === 0) {
				Reflect.deleteProperty(outfit.colors, property);
			}
		}
	}

	const _text = JSON.stringify(outfit);
	const _el = document.querySelector("#outfitItemExport-" + outfitIndex + " > a");
	const _done = function () {
		if (_el) {
			_el.textContent = "已复制";
			window.setTimeout(function () { if (_el) _el.textContent = "导出"; }, 2000);
		}
	};
	const _fallback = function () {
		try {
			const ta = document.createElement("textarea");
			ta.value = _text;
			ta.setAttribute("readonly", "readonly");
			ta.style.cssText = "position:fixed;left:6%;top:22%;width:88%;height:46%;z-index:99999;font-size:12px;padding:8px;";
			document.body.appendChild(ta);
			ta.focus();
			ta.select();
			try { ta.setSelectionRange(0, _text.length); } catch (e) {}
			let ok = false;
			try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
			const hint = document.createElement("div");
			hint.textContent = ok ? "已复制到剪贴板（点任意处关闭）" : "长按上面的文本全选复制（点任意处关闭）";
			hint.style.cssText = "position:fixed;left:6%;top:15%;z-index:99999;color:#fff;background:#333;padding:6px 10px;border-radius:4px;font-size:13px;";
			document.body.appendChild(hint);
			const close = function () {
				try { ta.remove(); hint.remove(); } catch (e) {}
				document.removeEventListener("click", close);
			};
			window.setTimeout(function () { document.addEventListener("click", close); }, 300);
			if (ok) _done();
			return ok;
		} catch (e) { return false; }
	};
	try {
		if (navigator.clipboard && navigator.clipboard.writeText) {
			navigator.clipboard.writeText(_text).then(_done).catch(_fallback);
		} else {
			_fallback();
		}
	} catch (e) {
		_fallback();
	}
}

'''
raw2 = raw[:i] + NEW + raw[j:]

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)

# 语法校验：把 twine-user-script 块抠出来 node --check
m = re.search(r'<script\b[^>]*id="twine-user-script"[^>]*>(.*?)</script>', raw2, re.S)
if not m:
    print("❌ 找不到 twine-user-script")
    sys.exit(1)
tmp = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
tmp.write(m.group(1))
tmp.close()
r = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
if r.returncode != 0:
    print("❌ JS 语法错误：", (r.stderr or "")[-800:])
    sys.exit(1)
print("✅ twine-user-script 语法 OK")

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入", HTML, len(raw2))
