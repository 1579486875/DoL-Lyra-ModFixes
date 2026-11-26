# -*- coding: utf-8 -*-
"""重新加回 POSSESSIVE_FIX（所有格）与 ARTICLE_FIX（冠词）。

背景：升级-作弊菜单补丁.py 的替换范围（START..END）把夹在中间的这两个补丁
      一起删掉了。这次插到 CHEAT_FACE_FIX_V2 段【之后】，远离未来的替换区间。
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "POSSESSIVE_FIX" in s or "ARTICLE_FIX" in s:
    print("⚠ 已存在，跳过")
    raise SystemExit(0)

BLOCK = r'''
	/* ============ 附加：文本清洗（所有格 + 冠词） ============ */
	/* 这两条处理「英文被部分替换成中文」后残留的英文成分。
	   与 CHEAT_FACE_FIX_V2 相邻但独立，避免被将来的段替换误删。 */

	/**
	 * 所有格残留：中文 + 's -> 中文 + 的
	 * 例：dogboy's 里 dogboy 被词表换成「狗男」，'s 留在原地 → 「狗男's」
	 */
	var POSSESSIVE_FIX = {
		re: /([\u4e00-\u9fff])(?:'s|’s)(?=[\s，。、；：！？,.;:!?）)」』"']|$)/g,
		to: '$1的'
	};

	/**
	 * 冠词残留：a/an/the + 中文
	 * 例：You are a catgirl. -> catgirl 换成「猫娘」后 a 留在原地 → 「你是 a 猫娘」
	 */
	var ARTICLE_FIX = [
		/* a/an + 中文 -> 「一个」+ 中文（比直接删自然） */
		{ re: /\b(?:a|an)\s+(?=[\u4e00-\u9fff])/gi, to: '一个' },
		/* the + 中文 -> 直接删（中文不需要定冠词） */
		{ re: /\bthe\s+(?=[\u4e00-\u9fff])/gi, to: '' }
	];

	function cleanTextNodes() {
		try {
			var $p = jQuery('#passages .passage').last();
			if (!$p.length) return;
			var walker = document.createTreeWalker($p[0], NodeFilter.SHOW_TEXT, null);
			var node, changed = 0;
			while ((node = walker.nextNode())) {
				var t = node.nodeValue;
				if (!t) continue;
				/* 快速跳过：既没有 's 也没有冠词就不处理 */
				if (!/['’]s|\b(?:a|an|the)\s/.test(t)) continue;
				var nt = t.replace(POSSESSIVE_FIX.re, POSSESSIVE_FIX.to);
				for (var i = 0; i < ARTICLE_FIX.length; i++) {
					nt = nt.replace(ARTICLE_FIX[i].re, ARTICLE_FIX[i].to);
				}
				if (nt !== t) {
					node.nodeValue = nt;
					changed++;
				}
			}
			if (changed > 0) log('文本清洗: ' + changed + ' 处');
		} catch (e) {}
	}

'''

# 插到 CHEAT_FACE_FIX_V2 段之后（找到 cheatFaceFixInstall 定义结束后的位置）
ANCHOR = "	/* 尽早安装：DOM 就绪即可 */"
if ANCHOR not in s:
    raise SystemExit("❌ 未找到插入锚点")

s2 = s.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert s2 != s

open(P, "w", encoding="utf-8").write(s2)
print("✅ 已加回，字符 %d -> %d" % (len(s), len(s2)))
print("   POSSESSIVE_FIX:", s2.count("POSSESSIVE_FIX"))
print("   ARTICLE_FIX   :", s2.count("ARTICLE_FIX"))
print("   cleanTextNodes:", s2.count("cleanTextNodes"))
