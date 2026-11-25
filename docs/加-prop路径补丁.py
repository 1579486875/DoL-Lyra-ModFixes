# -*- coding: utf-8 -*-
"""往「系统联动补全」追加：修复 prop 路径 undefined。

根因：
  BasicNeeds 把 toothbrush/soap/sponge 等日用品塞进 setup.foodstuff，
  但这些条目没有 prop_folder 字段；
  而 setup.props 里也没有它们，导致 !propErties.folder 成立，
  wearProp 走进 tending 分支执行 T.prop.folder = undefined，
  把 propDefaults 的 "general" 覆盖掉，路径变成 props/undefined/xxx.png。

修法：运行时给 setup.foodstuff 里缺 prop_folder 的日用品补 "general"。
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "PROP_FOLDER_FIX" in s:
    print("⚠ 已追加过，跳过")
    raise SystemExit(0)

EXTRA = r'''
	/* ============ 附加：prop 路径 undefined 修复 ============ */

	/**
	 * BasicNeeds 把日用品塞进 setup.foodstuff 时没写 prop_folder，
	 * 导致 wearProp 的 tending 分支把 T.prop.folder 覆盖成 undefined，
	 * 路径变成 img/clothes/props/undefined/xxx.png。
	 *
	 * 这里给这些条目补上正确的 prop_folder。
	 * 依据：这些图实际都在 img/clothes/props/general/ 下。
	 */
	var PROP_FOLDER_FIX = {
		// 日用品 -> 目录
		general: [
			'toothbrush', 'toothpaste', 'soap', 'sponge', 'bodywash', 'shampoo',
			'cup', 'water', 'bottle_water', 'comb', 'razor', 'towel', 'tissue',
			'sanitary_pad', 'tampon', 'condom', 'lube', 'hand_mirror', 'nail_clipper'
		]
	};

	function propFolderFix() {
		try {
			var fs = (typeof setup !== 'undefined') ? setup.foodstuff : null;
			if (!fs) return;
			var n = 0;
			for (var folder in PROP_FOLDER_FIX) {
				var list = PROP_FOLDER_FIX[folder];
				for (var i = 0; i < list.length; i++) {
					var k = list[i];
					var it = fs[k];
					if (it && typeof it === 'object' && !it.prop_folder) {
						it.prop_folder = folder;
						n++;
					}
				}
			}
			// 兜底：所有 foodstuff 条目若缺 prop_folder，按图是否存在于 general 推断
			for (var key in fs) {
				var item = fs[key];
				if (!item || typeof item !== 'object') continue;
				if (item.prop_folder) continue;
				// 只处理明显是日用品/手持类的（有 category 但没 prop_folder）
				if (item.category && /日用|洗漱|清洁|美容/.test(String(item.category))) {
					item.prop_folder = 'general';
					n++;
				}
			}
			if (n > 0) log('已补 prop_folder: ' + n + ' 项');
		} catch (e) {
			log('prop_folder 修复异常', e && e.message);
		}
	}

	/* setup 在游戏加载早期建立，这里每次渲染都检查一次（幂等，只补缺的） */
	jQuery(document).on(':passagerender', function () {
		setTimeout(function () {
			try { propFolderFix(); } catch (e) {}
		}, 30);
	});
'''

marker = "\twindow.系统联动 = {"
if marker not in s:
    raise SystemExit("❌ 未找到插入点")

s2 = s.replace(marker, EXTRA + "\n" + marker, 1)
open(P, "w", encoding="utf-8").write(s2)
print("✅ 已追加，长度 %d -> %d" % (len(s), len(s2)))
