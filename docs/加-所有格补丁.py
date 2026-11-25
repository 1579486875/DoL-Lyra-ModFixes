# -*- coding: utf-8 -*-
"""往「系统联动补全」追加：中文 + 's 所有格残留修正。

现象：「这只 狗男's 的主人总算把他拉走了」
原因：英文 dogboy's 里的 dogboy 被词表替换成「狗男」，但 's 没有对应处理，
      于是变成「狗男's」。
修法：渲染后扫描正文，把「中文+'s」统一改成「中文的」。
      只处理紧跟在中文后面的 's / ’s，避免误伤英文单词。
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "POSSESSIVE_FIX" in s:
    print("⚠ 已追加过，跳过")
    raise SystemExit(0)

EXTRA = r'''
	/* ============ 附加：中文 + 's 所有格残留 ============ */

	/**
	 * 英文 dogboy's 里的 dogboy 被词表替换成「狗男」，但 's 留下，
	 * 于是正文出现「狗男's 的主人」。
	 * 这里在渲染后把「中日韩字符 + 's」统一改成「…的」。
	 * 只在 \u4e00-\u9fff 后面匹配，不会误伤英文单词。
	 */
	var POSSESSIVE_FIX = {
		// 匹配：一个或多个 CJK 字符，紧跟 's / ’s，后面是空格/标点/行尾
		re: /([\u4e00-\u9fff])(?:'s|’s)(?=[\s，。、；：！？,.;:!?）)」』"']|$)/g
	};

	function possessiveFix() {
		try {
			var $p = jQuery('#passages .passage').last();
			if (!$p.length) return;
			var changed = 0;

			// 遍历文本节点，避免破坏 HTML 结构
			var walker = document.createTreeWalker($p[0], NodeFilter.SHOW_TEXT, null);
			var node;
			while ((node = walker.nextNode())) {
				var t = node.nodeValue;
				if (!t || t.indexOf("'s") < 0 && t.indexOf("’s") < 0) continue;
				var nt = t.replace(POSSESSIVE_FIX.re, '$1的');
				if (nt !== t) {
					node.nodeValue = nt;
					changed++;
				}
			}
			if (changed > 0) log('所有格修正: ' + changed + ' 处');
		} catch (e) {}
	}

	jQuery(document).on(':passagerender', function () {
		setTimeout(function () {
			try { possessiveFix(); } catch (e) {}
		}, 200);
	});
'''

marker = "\twindow.系统联动 = {"
if marker not in s:
    raise SystemExit("❌ 未找到插入点")

s2 = s.replace(marker, EXTRA + "\n" + marker, 1)
open(P, "w", encoding="utf-8").write(s2)
print("✅ 已追加，长度 %d -> %d" % (len(s), len(s2)))
