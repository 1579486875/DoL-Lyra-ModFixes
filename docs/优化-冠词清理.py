# -*- coding: utf-8 -*-
"""优化冠词清理：a/an + 中文 -> 「一个」+ 中文（而不是直接删）。

「你是 a 猫 女孩」→「你是一个猫 女孩」（比「你是 猫 女孩」自然）
the + 中文 -> 直接删（中文不需要定冠词）
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

OLD = '''	var ARTICLE_FIX = [
		/* a 后面紧跟中文（允许一个空格） */
		{ re: /\\b(?:a|an)\\s+(?=[\\u4e00-\\u9fff])/gi, to: '' },
		/* the 后面紧跟中文 */
		{ re: /\\bthe\\s+(?=[\\u4e00-\\u9fff])/gi, to: '' }
	];'''

NEW = '''	var ARTICLE_FIX = [
		/* a/an + 中文 -> 「一个」+ 中文（比直接删自然） */
		{ re: /\\b(?:a|an)\\s+(?=[\\u4e00-\\u9fff])/gi, to: '一个' },
		/* the + 中文 -> 直接删（中文不需要定冠词） */
		{ re: /\\bthe\\s+(?=[\\u4e00-\\u9fff])/gi, to: '' }
	];'''

if OLD in s:
    s2 = s.replace(OLD, NEW, 1)
elif 'to: \'\'' in s and 'ARTICLE_FIX' in s:
    # 宽松匹配：找到 a|an 那条规则改掉
    pat = re.compile(r"\{ re: /\\b\(\?:a\|an\)\\s\+\(\?=\[\\u4e00-\\u9fff\]\)/gi, to: '' \}")
    if pat.search(s):
        s2 = pat.sub("{ re: /\\b(?:a|an)\\s+(?=[\\u4e00-\\u9fff])/gi, to: '一个' }", s, count=1)
    else:
        print("❌ 未找到 a|an 规则")
        for mm in re.finditer(r"ARTICLE_FIX", s):
            print("  @%d" % mm.start())
        raise SystemExit(1)
else:
    raise SystemExit("❌ 未找到 ARTICLE_FIX")

assert s2 != s
open(P, "w", encoding="utf-8").write(s2)
print("✅ 已改为「一个」，长度 %d -> %d" % (len(s), len(s2)))

# 显示最终规则
i = s2.find("var ARTICLE_FIX")
print("\n=== 最终规则 ===")
print(s2[i:i + 400])
