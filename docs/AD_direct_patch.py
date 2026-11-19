"""直接注入补丁：不依赖 TweeReplacer，直接在 index.html 里做字符串替换。

用法：在 inject6.py 之后、rebuild2.py 之前运行。
"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# ---------- 1) 5 张汉化映射表 ----------
TYPES = [
    ("guardian", "监护人"), ("orphan", "孤儿"), ("student", "学生"), ("teacher", "教师"),
    ("headteacher", "校长"), ("librarian", "图书管理员"), ("shopkeeper", "店主"),
    ("police", "警察"), ("detective", "警探"), ("nurse", "护士"), ("doctor", "医生"),
    ("nun", "修女"), ("priest", "神父"), ("chef", "厨师"), ("baker", "面包师"),
    ("farmer", "农夫"), ("mechanic", "机械师"), ("hunter", "猎人"),
    ("wanderer", "流浪者"), ("stranger", "陌生人"), ("landlord", "房东"),
    ("bartender", "酒保"), ("waiter", "服务员"), ("waitress", "女服务员"),
    ("cow", "奶牛"), ("bull", "公牛"), ("wolf", "狼"), ("snake", "蛇"),
    ("dog", "狗"), ("cat", "猫"), ("fox", "狐狸"), ("bear", "熊"),
    ("bird", "鸟"), ("horse", "马"), ("pig", "猪"), ("sheep", "羊"),
    ("eel", "鳗鱼"), ("eels", "鳗鱼"), ("slime", "史莱姆"), ("slimes", "史莱姆"),
    ("worm", "蠕虫"), ("worms", "蠕虫"), ("spider", "蜘蛛"), ("spiders", "蜘蛛"),
    ("slug", "蛞蝓"), ("slugs", "蛞蝓"), ("maggot", "蛆虫"), ("maggots", "蛆虫"),
    ("squid", "乌贼"), ("wasp", "黄蜂"), ("bee", "蜜蜂"), ("bees", "蜜蜂"),
    ("lurker", "潜伏者"), ("vine", "藤蔓"), ("tentacle", "触手"),
    ("fish", "鱼"), ("human", "人类"), ("pup", "幼崽"), ("puppy", "小狗"),
    ("kitten", "小猫"), ("cub", "幼兽"), ("creature", "生物"), ("beast", "野兽"),
]

NAMES = [
    ("Avery", "艾弗里"), ("Bailey", "贝利"), ("Briar", "布莱尔"), ("Charlie", "查理"),
    ("Darryl", "达里尔"), ("Doren", "多伦"), ("Eden", "伊甸"), ("Gwylan", "格威岚"),
    ("Harper", "哈珀"), ("Jordan", "乔丹"), ("Kylar", "凯拉"), ("Landry", "兰德里"),
    ("Leighton", "礼顿"), ("Mason", "梅森"), ("Morgan", "摩根"), ("River", "里弗"),
    ("Robin", "罗宾"), ("Sam", "山姆"), ("Sirris", "茜里斯"), ("Sydney", "悉尼"),
    ("Whitney", "惠特尼"), ("Wren", "雷恩"), ("Alex", "亚历克斯"), ("Quinn", "奎恩"),
    ("Remy", "雷米"), ("Niki", "妮基"), ("Winter", "温特"), ("Zephyr", "泽菲尔"),
    ("Seath", "希斯"), ("Alice", "爱丽丝"), ("Liddell", "利德尔"),
    ("Rowan", "罗文"), ("Adrian", "阿德里安"), ("Grant", "格兰特"),
    ("Moonfeather", "月羽"), ("Night Monster", "夜魔"),
    ("Black Wolf", "黑狼"), ("Great Hawk", "巨鹰"), ("Ivory Wraith", "象牙幽魂"),
]

AREAS = [
    ("Orphanage", "孤儿院"), ("Bedroom", "卧室"), ("Barb Street", "巴布街"),
    ("Cliff Street", "悬崖街"), ("Connudatus Street", "康努达图斯街"),
    ("Danube Street", "多瑙街"), ("Domus Street", "多姆斯街"), ("Elk Street", "麋鹿街"),
    ("Harvest Street", "丰收街"), ("High Street", "高街"), ("Mer Street", "梅尔街"),
    ("Nightingale Street", "夜莺街"), ("Oxford Street", "牛津街"),
    ("Starfish Street", "海星街"), ("Wolf Street", "狼街"),
    ("Residential Alleyways", "住宅区小巷"), ("Commercial Alleyways", "商业区小巷"),
    ("Industrial Alleyways", "工业区小巷"), ("Park", "公园"), ("Hallways", "走廊"),
    ("Brothel", "妓院"), ("Strip Club", "脱衣舞俱乐部"), ("Beach", "海滩"),
    ("Ocean Breeze", "海风咖啡厅"), ("Docks Work", "码头工作区"),
    ("Residential Drain", "住宅区下水道"), ("Commercial Drain", "商业区下水道"),
    ("Industrial Drain", "工业区下水道"), ("Forest", "森林"), ("Farmland", "农田"),
    ("Livestock Field", "畜牧场"), ("Moor", "荒原"), ("Forest Wolf Cave", "森林狼洞"),
    ("Wolf Cave", "狼洞"), ("Wolf Cave Clearing", "狼洞空地"), ("Asylum", "疯人院"),
    ("Asylum Cell", "疯人院牢房"), ("Underground Cell", "地下牢房"),
    ("Prison Cell", "监狱牢房"), ("Island", "岛屿"), ("Eden Cabin", "伊甸小屋"),
    ("Bird Tower", "鹰塔"),
]

FOODS = [
    ("coffee", "咖啡"), ("tea", "茶"), ("hot chocolate", "热巧克力"),
    ("milkshake", "奶昔"), ("smoothie", "冰沙"), ("water", "水"),
    ("sandwich", "三明治"), ("cake", "蛋糕"), ("pie", "派"),
    ("cookie", "饼干"), ("muffin", "松饼"), ("croissant", "牛角包"),
    ("scone", "司康"), ("toast", "吐司"), ("salad", "沙拉"), ("soup", "汤"),
]


def join(pairs):
    return "|".join(k + "," + v for k, v in pairs)


# ---------- 2) 关系值名（statDefaults） ----------
STAT_MAP = {
    "Lust": "性欲", "Dominance": "支配", "Trauma": "创伤", "Rage": "愤怒",
    "Purity": "纯洁", "Corruption": "堕落", "Harmony": "和谐",
}
LOVE_ALIAS = {
    "Affection": "好感", "Interest": "兴趣", "Respect": "尊敬",
    "Liking": "好感", "Devotion": "忠诚", "Love": "爱意",
}

# ---------- 3) 脸型名 ----------
FACE_VARIANT_CN = {
    "default": "温柔", "catty": "妩媚", "aloof": "高冷",
    "sweet": "甜美", "foxy": "勾人", "gloomy": "忧郁",
    "makeup": "妆容", "modded1": "模组1",
}


def esc(s):
    return H.escape(s, quote=False)


def apply(data, old, new, label, required=True):
    """在转义后的 HTML 里替换；old/new 用未转义文本，内部自动转义。"""
    e_old = esc(old)
    e_new = esc(new)
    if e_old in data:
        data = data.replace(e_old, e_new, 1)
        print(f"  ✅ {label}")
        return data, True
    # 尝试未转义
    if old in data:
        data = data.replace(old, new, 1)
        print(f"  ✅ {label}（未转义形态）")
        return data, True
    print(f"  ❌ {label}  未命中")
    if required:
        return data, False
    return data, False


def main():
    src = open(HTML, "rb").read().decode("utf-8", "replace")
    data = src
    ok = 0
    fail = []

    # ---- A) 5 张表 + bodyShapescn：挂在 bodyShapes 后面 ----
    anchor = '<<set setup.bodyShapes to ["classic", "slender", "curvy", "soft"]>>'
    inject = (anchor
              + '<<set setup.bodyShapescn to {"经典": "classic", "瘦长": "slender", "曲线": "curvy", "柔软": "soft"}>>'
              + '<<set setup.NPCTypeList_cn_name to "' + join(TYPES) + '">>'
              + '<<set setup.NPCNameList_cn_name to "' + join(NAMES) + '">>'
              + '<<set setup.NPCTitleList_cn_name to "' + join(TYPES) + '">>'
              + '<<set setup.majorAreas_cn_name to "' + join(AREAS) + '">>'
              + '<<set setup.CafeFoodList_cn_name to "' + join(FOODS) + '">>')
    data, hit = apply(data, anchor, inject, "5 张汉化映射表 + bodyShapescn")
    ok += hit
    if not hit:
        fail.append("映射表")

    # ---- B) relation-box 的名字块 ----
    box_old = """<span class="relation-name">
						_npcData.nam
						<small class="relation-title black"><i>The _npcData.title</i></small>
					</span>"""
    box_new = """<span class="relation-name">
						<<= window.npcNameCN ? window.npcNameCN(_npcData["nam"]) : _npcData["nam"]>>
						<small class="relation-title black"><i>The <<= window.npcTitleCN ? window.npcTitleCN(_npcData["title"]) : _npcData["title"]>></i></small>
					</span>"""
    data, hit = apply(data, box_old, box_new, "relation-box 名字块", required=False)
    ok += hit
    if not hit:
        fail.append("relation-box")

    # ---- C) 关系值名 ----
    for en, cn in LOVE_ALIAS.items():
        pass  # loveAlias 是函数表，改用下面的 statNameCN 包裹

    for en, cn in STAT_MAP.items():
        o = 'name : "' + en + '",'
        n = 'name : (window.statNameCN ? window.statNameCN("' + en + '") : "' + en + '"),'
        data, hit = apply(data, o, n, f"statDefaults {en}", required=False)
        ok += hit
        if not hit:
            # 试 name:（无空格）
            o2 = 'name: "' + en + '",'
            n2 = 'name : (window.statNameCN ? window.statNameCN("' + en + '") : "' + en + '"),'
            data, hit2 = apply(data, o2, n2, f"statDefaults {en}(紧凑)", required=False)
            ok += hit2
            if not hit2:
                fail.append(f"stat:{en}")

    # love 列
    love_old = 'name : setup.loveAlias[T.npcData.nam](),'
    love_new = 'name : (window.statNameCN ? window.statNameCN(setup.loveAlias[T.npcData.nam]()) : setup.loveAlias[T.npcData.nam]()),'
    data, hit = apply(data, love_old, love_new, "statDefaults love", required=False)
    ok += hit
    if not hit:
        fail.append("stat:love")

    # ---- D) 脸型选项的中文 ----
    # setup.faceVariantOptions 的键已经是中文（i18n 干过），只需处理 makeup 等
    # 这里给 cheatsDemeanour 的显示加兜底
    dem_old = "<<link _faceVariants[_i].toUpperFirst()>>"
    dem_new = "<<link (window.faceVariantLabel ? window.faceVariantLabel(_i, (typeof _faceVariantscn !== 'undefined' ? _faceVariantscn : null), _faceVariants) : _faceVariants[_i])>>"
    data, hit = apply(data, dem_old, dem_new, "cheatsDemeanour 兜底", required=False)
    ok += hit

    # ---- E) 状态名 Drunk ----
    for en, cn in [("Drunk", "醉酒"), ("Drugs", "药物"), ("Hallucinogens", "致幻")]:
        o = '<<numberStepper "' + en + '"'
        n = '<<numberStepper "' + cn + '"'
        data, hit = apply(data, o, n, f"状态名 {en}", required=False)
        ok += hit

    # ---- F) 狼群声誉名 ----
    for en, cn in [("Wolf Pack Harmony", "狼群·和谐"), ("Wolf Pack Ferocity", "狼群·凶性"),
                   ("Harmony", "和谐"), ("Ferocity", "凶性")]:
        o = 'name : "' + en + '"'
        n = 'name : (window.statNameCN ? window.statNameCN("' + en + '") : "' + en + '")'
        data, hit = apply(data, o, n, f"声誉名 {en}", required=False)
        ok += hit

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n合计命中 {ok} 项")
    if fail:
        print("未命中：", fail)
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
