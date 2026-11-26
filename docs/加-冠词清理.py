# -*- coding: utf-8 -*-
"""修「英文冠词残留」：a / an / the + 中文 → 中文。

现象：「你是 a 猫 女孩」（原文 You are a catgirl）
根因：词表把 catgirl 换成中文，但英文冠词 a/an/the 没有处理。

修法：在已有的 POSSESSIVE_FIX 里加冠词清理规则，同样只处理「冠词紧邻中文」的情况，
避免误伤英文原文（如 "a" 在纯英文句子里不该动）。
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "ARTICLE_FIX" in s:
    print("⚠ 已追加过，跳过")
    raise SystemExit(0)

# 在 POSSESSIVE_FIX 定义之后插入冠词规则
ANCHOR = "\tvar POSSESSIVE_FIX = {"
if ANCHOR not in s:
    raise SystemExit("❌ 未找到 POSSESSIVE_FIX")

EXTRA = r'''
	/* ============ 附加：英文冠词残留（a / an / the + 中文） ============ */

	/**
	 * 原文 "You are a catgirl." 里 catgirl 被换成「猫娘」，
	 * 但冠词 a 留在原处 → 「你是 a 猫娘」。
	 * 这里清理「冠词 + 空格 + 中文字符」的组合。
	 *
	 * 规则（按顺序应用）：
	 *   a/an + 中文  -> 中文        （中文不需要不定冠词）
	 *   the + 中文   -> 中文        （同上）
	 * 只在冠词紧邻中文、且有空格分隔时处理，纯英文语境不动。
	 */
	var ARTICLE_FIX = [
		/* a 后面紧跟中文（允许一个空格） */
		{ re: /\b(?:a|an)\s+(?=[\u4e00-\u9fff])/gi, to: '' },
		/* the 后面紧跟中文 */
		{ re: /\bthe\s+(?=[\u4e00-\u9fff])/gi, to: '' }
	];

	function articleFix() {
		try {
			var $p = jQuery('#passages .passage').last();
			if (!$p.length) return;
			var changed = 0;

			var walker = document.createTreeWalker($p[0], NodeFilter.SHOW_TEXT, null);
			var node;
			while ((node = walker.nextNode())) {
				var t = node.nodeValue;
				if (!t) continue;
				/* 快速跳过：没有冠词就不处理 */
				if (!/\b(?:a|an|the)\s/.test(t)) continue;
				var nt = t;
				for (var i = 0; i < ARTICLE_FIX.length; i++) {
					nt = nt.replace(ARTICLE_FIX[i].re, ARTICLE_FIX[i].to);
				}
				if (nt !== t) {
					node.nodeValue = nt;
					changed++;
				}
			}
			if (changed > 0) log('冠词残留清理: ' + changed + ' 处');
		} catch (e) {}
	}

'''

s2 = s.replace(ANCHOR, EXTRA + ANCHOR, 1)

# 把 articleFix 加进 :passagerender 调用（复用 POSSESSIVE_FIX 那个监听）
CALL_ANCHOR = "\t\t\ttry { possessiveFix(); } catch (e) {}"
if CALL_ANCHOR in s2:
    s2 = s2.replace(CALL_ANCHOR,
                    CALL_ANCHOR + "\n\t\t\ttry { articleFix(); } catch (e) {}",
                    1)
    print("✅ articleFix 已挂到 passagerender")
else:
    print("⚠ 未找到 possessiveFix 调用点，需手动挂")

open(P, "w", encoding="utf-8").write(s2)
print("✅ 已追加，长度 %d -> %d" % (len(s), len(s2)))
