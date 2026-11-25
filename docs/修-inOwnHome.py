# -*- coding: utf-8 -*-
"""修 inOwnHome()：realEstate.current 是「拥有的房产」不是「当前所在地」。

原实现 if (cur) return true —— 只要玩家有房产就永远判定为「在家」，
导致 onHomeRelief() 在公园/街道也会触发，把「反正是自己家…」的旁白插进无关段落。

修法：
1) 先用 passage 白名单（最可靠）
2) 再用 $location === 'home' 辅助
3) 最后才用 realEstate.current，但必须与当前 passage 的房产名匹配，不能直接 true
"""
import re

P = r"E:\TAML\_dol\work\联动模组\系统联动补全\scripts\core.js"
s = open(P, encoding="utf-8").read()

if "inOwnHome 修正版" in s:
    print("⚠ 已修过，跳过")
    raise SystemExit(0)

# 定位原函数
m = re.search(r"function inOwnHome\(\)\s*\{", s)
if not m:
    raise SystemExit("❌ 未找到 inOwnHome")

start = s.index("{", m.start())
depth = 0
i = start
while i < len(s):
    if s[i] == "{":
        depth += 1
    elif s[i] == "}":
        depth -= 1
        if depth == 0:
            break
    i += 1
old_fn = s[m.start():i + 1]
print("原函数:")
print(old_fn)

NEW_FN = '''function inOwnHome() {
		/* inOwnHome 修正版
		 * 旧实现 `if (realEstate.current) return true` 把「拥有房产」当成了「身处家中」，
		 * 只要有房就永远判定在家，导致 onHomeRelief() 在公园/街道也触发，
		 * 把「反正是自己家…」的旁白插进无关段落。
		 * 现在：passage 白名单 > $location === 'home' > 房产名与当前 passage 匹配。 */
		var p = currentPassage();

		// 1) 确定的房产 passage 白名单（最可靠）
		if (/Deadwood Reblooms|Flats Own (Room|Shower|Bath)|Orphanage Bedroom|Orphanage Bathroom|Cottage Interior|Manor Bedroom/i.test(p)) {
			return true;
		}

		// 2) 原版 $location 标记（家 = "home"；孤儿院浴室/卧室都设为 home）
		var loc = safe(function () { return V.location; }, null);
		if (typeof loc === 'string' && loc === 'home') return true;

		// 3) 房产名与当前 passage 名做包含匹配（支持 LocationsExt 动态房产），
		//    绝不再「有房就 true」
		var cur = safe(function () {
			return maplebirch && maplebirch.get && maplebirch.get('Finance').realEstate.current;
		}, null);
		if (cur) {
			var nm = '';
			try {
				nm = typeof cur === 'string' ? cur : (cur.name || cur.label || '');
			} catch (e) { nm = ''; }
			if (nm && p && p.toLowerCase().indexOf(String(nm).toLowerCase()) >= 0) return true;
		}

		return false;
	}'''

s2 = s[:m.start()] + NEW_FN + s[i + 1:]
open(P, "w", encoding="utf-8").write(s2)
print("\n✅ 已替换，长度 %d -> %d" % (len(s), len(s2)))
