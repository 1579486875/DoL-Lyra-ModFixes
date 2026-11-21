"""AW03（第13轮）：Npc Name CN 1.3.1 → 1.4.0 —— 查名优先用官方汉化的映射表（幂等，改包内模组）。

问题（第13轮运行时探针实测）：
  Npc Name CN 1.3.0 起「强制接管」setup.NPC_CN_NAME / NPC_CN_TYPE / NPC_CN_TITLE，
  只查自己内置的 39 名 + 60 类小表，官方的 setup.NPCTypeList_cn_name（248 类）/ NPCNameList_cn_name /
  NPCTitleList_cn_name 被完全绕过：
    · 钓鱼开场「herring咬住了钩上的黑莓」—— 15 种鱼名全是英文（官方表里都有：鲱鱼/鳕鱼/鳟鱼…）；
    · 另有 194 个类型键只靠 EXTRA 兜底，没兜到的显示英文；
    · 名字与正文不一致（内置表 Jordan=乔丹，官方与正文 520 处都是「约旦」）。
修法（①保意图）：查找顺序改为「官方表 → 内置表 → 原样返回」，仍保证「查得到就中文、查不到就原样」，不污染数据。
  官方表的已知错译单独覆盖：fish → 鱼（官方表写成「海星」）。
  官方表按字符串内容缓存，表被改写时自动重新解析。
"""
import json
import os
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AW03] index 形态异常")
    sys.exit(1)

MOD = "Npc Name CN"
MARK = "/* [AW03] official-table-first */"
OLD = ("\tfunction nameCN(v) { return tr(NAMES, v); }\n"
       "\tfunction typeCN(v) { return tr(TITLES, v); }\n"
       "\tfunction titleCN(v) { return tr(TITLES, v); }\n")
NEW = MARK + """
	/* 1.4.0：先查官方汉化的映射表（setup.NPCNameList_cn_name 等，| 分隔的 "英文,中文" 串），
	 * 查不到再用内置表；表内容变化时重新解析。 */
	/* fish：官方类型表写成了「海星」；baitfish：官方类型表没有，取官方 foodstuff.js 的译名「饵鱼」 */
	var OFFICIAL_FIX = { "fish": "鱼", "baitfish": "饵鱼" };
	var _tbl = {};
	function officialTable(key) {
		try {
			var st = window.SugarCube && window.SugarCube.setup;
			var raw = st ? st[key] : null;
			if (typeof raw !== "string" || !raw) return null;
			var c = _tbl[key];
			if (c && c.raw === raw) return c.map;
			var map = {};
			raw.split("|").forEach(function (pair) {
				var i = pair.indexOf(",");
				if (i < 0) return;
				var k = pair.slice(0, i).trim(), v = pair.slice(i + 1).trim();
				if (k && v && !Object.prototype.hasOwnProperty.call(map, k.toLowerCase())) map[k.toLowerCase()] = v;
			});
			_tbl[key] = { raw: raw, map: map };
			return map;
		} catch (e) { return null; }
	}
	function trOfficial(tableKeys, fallback, key) {
		if (key === undefined || key === null) return "";
		var s = String(key);
		var low = s.toLowerCase().trim();
		if (Object.prototype.hasOwnProperty.call(OFFICIAL_FIX, low)) return OFFICIAL_FIX[low];
		for (var i = 0; i < tableKeys.length; i++) {
			var t = officialTable(tableKeys[i]);
			if (t && Object.prototype.hasOwnProperty.call(t, low)) return t[low];
		}
		return tr(fallback, s);
	}
	function nameCN(v) { return trOfficial(["NPCNameList_cn_name"], NAMES, v); }
	function typeCN(v) { return trOfficial(["NPCTypeList_cn_name"], TITLES, v); }
	function titleCN(v) { return trOfficial(["NPCTitleList_cn_name", "NPCTypeList_cn_name"], TITLES, v); }
"""

js = MZ.read_mod_file(data, MOD, "npcNameCN.js")
if js is None:
    print("[AW03] FAIL 包内找不到 %s/npcNameCN.js" % MOD)
    sys.exit(1)
if MARK in js.decode("utf-8"):
    print("[AW03] 已存在，跳过")
    sys.exit(0)
if OLD not in js.decode("utf-8"):
    print("[AW03] FAIL 锚点不匹配（npcNameCN.js 结构已变）")
    sys.exit(1)

DESC_ADD = ("1.4.0（DoL-Lyra-ModFixes 第13轮）：查名改为「官方汉化映射表优先」——setup.NPCTypeList_cn_name（248 类，含 15 种鱼名）"
            " / NPCNameList_cn_name / NPCTitleList_cn_name 查不到时才用内置表，修复钓鱼等处物种名显示英文、"
            "角色名与正文译名不一致（如 Jordan 乔丹→约旦）的问题；官方表把 fish 写成「海星」，单独改回「鱼」。")


def fn(name, b):
    if name == "npcNameCN.js":
        s = b.decode("utf-8").replace(OLD, NEW, 1).replace("/* NpcNameCN 1.3.0", "/* NpcNameCN 1.4.0", 1)
        return s.encode("utf-8")
    if name == "boot.json":
        bj = json.loads(b.decode("utf-8-sig"))
        bj["version"] = "1.4.0"
        if DESC_ADD not in bj.get("description", ""):
            bj["description"] = bj.get("description", "") + " " + DESC_ADD
        return json.dumps(bj, ensure_ascii=False, indent=2).encode("utf-8")
    return None


data, changed = MZ.patch_mod(data, MOD, fn)
if sorted(changed) != ["boot.json", "npcNameCN.js"]:
    print("[AW03] FAIL 改写结果异常: %s" % changed)
    sys.exit(1)
open(HTML, "wb").write(data.encode("utf-8"))
print("[AW03] Npc Name CN → 1.4.0  OK")
