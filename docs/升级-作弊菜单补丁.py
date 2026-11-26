# -*- coding: utf-8 -*-
"""修作弊菜单 FaceStyle/Demeanour 的 undefined：
1) 改用 MutationObserver（作弊菜单是 overlay，不触发 :passagerender）
2) 按 setup.faceStyleOptions / faceVariantOptions 的真实键名做映射（中文键）
3) 兜底：直接把 undefined 换成有意义的文本
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "CHEAT_FACE_FIX_V2" in s:
    print("⚠ 已升级过，跳过")
    raise SystemExit(0)

# 定位旧的 CHEAT_FACE_FIX 段（从注释到 window.系统联动 = {）
START = "\t/* ============ 附加：作弊菜单脸型/举止显示修复 ============ */"
END = "\twindow.系统联动 = {"

i = s.find(START)
j = s.find(END)
if i < 0 or j < 0 or j < i:
    raise SystemExit("❌ 未找到旧补丁段")

NEW = r'''	/* ============ 附加：作弊菜单脸型/举止显示修复 v2 ============ */

	/**
	 * 作弊菜单「状态 → 玩家 → 身体」两处 undefined：
	 *
	 *  cheatsFaceStyle widget:
	 *      <<set _faceStyles to Object.values(setup.faceStyleOptions)>>
	 *      <<link _faceStylescn[_i]>>        ← _faceStylescn 从未赋值
	 *  cheatsDemeanour widget:
	 *      <<link _faceVariantscn[_i]>>      ← 同样未赋值
	 *
	 *  setup.faceStyleOptions 的真实结构是 { "传统": "default" }（中文键 → 内部值），
	 *  setup.faceVariantOptions 是 { "default": { "温柔": "default", ... "妆容": "makeup" } }。
	 *
	 *  v1 的问题：只在 :passagerender 里跑，而作弊菜单是 overlay 弹层，
	 *  打开时【不触发】passagerender，所以补丁从来没执行过。
	 *  v2 改用 MutationObserver 监听 body 变化 + setInterval 兜底。
	 */
	var CHEAT_FACE_FIX_V2 = {
		installed: false,
		/* 内部值 → 中文（与 setup 里的映射方向相反，用于把英文内部值翻回中文） */
		variantCN: {
			'default': '温柔', 'catty': '妩媚', 'aloof': '高冷',
			'sweet': '甜美', 'foxy': '勾人', 'gloomy': '忧郁',
			'makeup': '妆容', 'Makeup': '妆容'
		},
		styleCN: {
			'default': '传统'
		}
	};

	function cheatFaceFix2() {
		try {
			/* —— 面部风格 —— */
			var el = document.getElementById('statsFaceStyle');
			if (el) {
				var t = String(el.textContent || '').trim();
				if (!t || t === 'undefined' || t === 'null') {
					var raw = '';
					try { raw = String(V.facestyle || 'default'); } catch (e) {}
					el.textContent = CHEAT_FACE_FIX_V2.styleCN[raw] || raw || '传统';
				} else if (CHEAT_FACE_FIX_V2.styleCN[t.toLowerCase()]) {
					el.textContent = CHEAT_FACE_FIX_V2.styleCN[t.toLowerCase()];
				}
			}

			/* —— 举止：可能是多个 <a>/<span> 用 | 分隔 —— */
			var dm = document.getElementById('statsDemeanour');
			if (dm) {
				var nodes = dm.querySelectorAll('a, span');
				var handled = false;
				for (var k = 0; k < nodes.length; k++) {
					var n = nodes[k];
					if (n.children.length) continue;      /* 只处理叶子 */
					var tx = String(n.textContent || '').trim();
					if (!tx) continue;
					var low = tx.toLowerCase();
					if (CHEAT_FACE_FIX_V2.variantCN[low]) {
						n.textContent = CHEAT_FACE_FIX_V2.variantCN[low];
						handled = true;
					} else if (tx === 'undefined' || tx === 'null') {
						n.textContent = '温柔';
						handled = true;
					}
				}
				/* 兜底：整块文本里裸露的英文单词 */
				if (!handled) {
					var html = dm.innerHTML || '';
					var changed = false;
					for (var kk in CHEAT_FACE_FIX_V2.variantCN) {
						var cn = CHEAT_FACE_FIX_V2.variantCN[kk];
						var reW = new RegExp('(^|[>\\s|｜、])' + kk + '($|[<\\s|｜、])', 'g');
						var nh = html.replace(reW, function (all, a, b) { return a + cn + b; });
						if (nh !== html) { html = nh; changed = true; }
					}
					if (changed) dm.innerHTML = html;
				}
			}
		} catch (e) {}
	}

	function cheatFaceFixInstall() {
		if (CHEAT_FACE_FIX_V2.installed) return;
		CHEAT_FACE_FIX_V2.installed = true;

		/* 方式1：MutationObserver —— 作弊菜单打开会往 body 插节点，能捕获 */
		try {
			var obs = new MutationObserver(function () {
				cheatFaceFix2();
			});
			obs.observe(document.body, { childList: true, subtree: true });
		} catch (e) {}

		/* 方式2：定时兜底（作弊菜单可能只改文本不改结构） */
		setInterval(function () {
			if (document.getElementById('statsFaceStyle') || document.getElementById('statsDemeanour')) {
				cheatFaceFix2();
			}
		}, 1200);

		log('作弊菜单脸型补丁 v2 已安装（MutationObserver + 定时兜底）');
	}

	/* 尽早安装：DOM 就绪即可 */
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', cheatFaceFixInstall);
	} else {
		cheatFaceFixInstall();
	}

'''

s2 = s[:i] + NEW + s[j:]
open(P, "w", encoding="utf-8").write(s2)
print("✅ 已替换为 v2，长度 %d -> %d" % (len(s), len(s2)))
