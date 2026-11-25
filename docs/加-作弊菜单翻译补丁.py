# -*- coding: utf-8 -*-
"""往「系统联动补全」追加：修正作弊菜单的脸型/举止显示。

问题：
1) 作弊菜单写 <<if setup.faceStyleOptions.length gt 1>>，
   但它是对象、.length 恒为 undefined → 判断失真，且 <<cheatsFaceStyle>> 可能输出 undefined。
2) 举止走 i18n 硬编码的 _faceVariantscn[_i]（6 项），
   新版 facevariant 可能是 7 项（多一个 makeup）→ 越界输出英文/undefined。
3) Cheat Face Fix 模组只定义了 faceStyleCN / faceVariantLabel 两个函数，
   但 tweeFileList 与 addonPlugin 都是空的，从未被调用。

修法：每次渲染后直接修 DOM 里的 #statsFaceStyle / #statsDemeanour，
按可用映射把 undefined 与英文替换成中文。
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "CHEAT_FACE_FIX" in s:
    print("⚠ 已追加过，跳过")
    raise SystemExit(0)

EXTRA = r'''
	/* ============ 附加：作弊菜单脸型/举止显示修复 ============ */

	/**
	 * 作弊菜单「状态 → 玩家 → 身体」两处显示问题：
	 *  1) #statsFaceStyle 可能显示 undefined（setup.faceStyleOptions 是对象，
	 *     原版用 .length 判断失真，且值本身可能没中文）
	 *  2) #statsDemeanour 里的举止走 i18n 硬编码 _faceVariantscn[_i]（6 项），
	 *     新版 facevariant 有 7 项（多 makeup）→ 越界显示英文
	 *
	 * Cheat Face Fix 模组本意是修这个，但它的 tweeFileList / addonPlugin 都是空的，
	 * 只定义了函数没接进去。这里直接在 DOM 层兜底。
	 */
	var CHEAT_FACE_FIX = {
		// 脸型（faceStyle）中文
		style: {
			'default': '传统'
		},
		// 举止（facevariant）中文 —— 覆盖新版 7 项
		variant: {
			'default': '朴素',
			'catty': '娇嗔',
			'aloof': '高冷',
			'sweet': '甜美',
			'foxy': '妩媚',
			'gloomy': '忧郁',
			'makeup': '妆容',
			'Makeup': '妆容'
		}
	};

	function cheatFaceFix() {
		try {
			var p = currentPassage();
			// 只在作弊菜单相关页面处理
			if (!/cheat|Cheat|作弊/i.test(p)) {
				// 也检查 DOM 是否存在目标节点
				if (!document.querySelector('#statsFaceStyle, #statsDemeanour')) return;
			}

			// 1) 脸型
			var $fs = jQuery('#statsFaceStyle');
			if ($fs.length) {
				var t = String($fs.text() || '').trim();
				if (!t || t === 'undefined' || t === 'null') {
					var raw = '';
					try { raw = String(V.facestyle || 'default'); } catch (e) {}
					$fs.text(CHEAT_FACE_FIX.style[raw] || raw || '传统');
				} else if (CHEAT_FACE_FIX.style[t.toLowerCase()]) {
					$fs.text(CHEAT_FACE_FIX.style[t.toLowerCase()]);
				}
			}

			// 2) 举止（可能是多个按钮/文本混排）
			var $dm = jQuery('#statsDemeanour');
			if ($dm.length) {
				$dm.find('button, span, a').addBack().each(function () {
					var $n = jQuery(this);
					var txt = String($n.text() || '').trim();
					if (!txt) return;
					// 整词替换：Makeup / Default / Catty ...
					var low = txt.toLowerCase();
					if (CHEAT_FACE_FIX.variant[low]) {
						// 保留原有分隔符结构时只替换文本节点
						if ($n.children().length === 0) $n.text(CHEAT_FACE_FIX.variant[low]);
					} else if (txt === 'undefined' || txt === 'null') {
						$n.text('朴素');
					}
				});
				// 兜底：把整块里裸露的英文单词换掉（不碰标签）
				var html = $dm.html() || '';
				var changed = false;
				for (var k in CHEAT_FACE_FIX.variant) {
					var cn = CHEAT_FACE_FIX.variant[k];
					var reW = new RegExp('(^|[>\\s|｜、])' + k + '($|[<\\s|｜、])', 'g');
					var nhtml = html.replace(reW, function (all, a, b) { return a + cn + b; });
					if (nhtml !== html) { html = nhtml; changed = true; }
				}
				if (changed) $dm.html(html);
			}
		} catch (e) {}
	}

	jQuery(document).on(':passagerender', function () {
		setTimeout(function () {
			try { cheatFaceFix(); } catch (e) {}
		}, 220);   // 晚于其它模组，确保 DOM 已定稿
	});
'''

marker = "\twindow.系统联动 = {"
if marker not in s:
    raise SystemExit("❌ 未找到插入点")

s2 = s.replace(marker, EXTRA + "\n" + marker, 1)
open(P, "w", encoding="utf-8").write(s2)
print("✅ 已追加，长度 %d -> %d" % (len(s), len(s2)))
