"""AC06：翻译 256 个成就名（只在 setup.feats 块内替换 title 字段）。

关键：title 这个字段名在别处也有（如 setup.NPCTitleList），
      所以必须限定在 setup.feats = { ... } 块内替换。
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AC06] index 形态异常")
    sys.exit(1)

MARK = "[AC06]"
g0 = H.unescape(data)
if MARK in g0:
    print("[AC06] 已存在，跳过")
    sys.exit(0)

MAP = {
    "Pocket Change": "零钱",
    "Money Maker": "赚钱能手",
    "Tycoon": "商业大亨",
    "Millionaire": "百万富翁",
    "It Belongs in a Museum!": "它该进博物馆！",
    "Fully Covered": "全副武装",
    "Being a Boy": "身为男孩",
    "Being a Girl": "身为女孩",
    "Being a Hermaphrodite": "身为雌雄同体",
    "Being an Orphan": "身为孤儿",
    "Stressful Challenge": "压力挑战",
    "Long Stressful Challenge": "漫长的压力挑战",
    "Billboard": "广告牌",
    "A Living Canvas": "活体画布",
    "Farmhand": "农场工人",
    "Farmer": "农夫",
    "Cultivator": "耕种者",
    "The Rival Farm": "对手农场",
    "The Rival Estate": "对手庄园",
    "Heroic Victory": "英雄式胜利",
    "Five in a Row": "五连胜",
    "Distinction": "卓越",
    "Distinctive": "出众",
    "Distinguished": "声名显赫",
    "Chef de Tournant": "轮值主厨",
    "Chef de Partie": "部门主厨",
    "Sous Chef": "副主厨",
    "Science Fair Winner": "科学展冠军",
    "Thesis Offence": "论文违规",
    "Maths Competition Winner": "数学竞赛冠军",
    "Rich Hearts": "富有的心",
    "50 Shades of Tan": "五十度棕",
    "Most Aware": "最警觉",
    "Most Innocent": "最纯真",
    "No More Control": "失控",
    "Thief": "窃贼",
    "May I Have This Dance?": "能赏脸跳一曲吗？",
    "Aquanaut": "潜水员",
    "Seductress": "妖妇",
    "Green Fingered": "园艺高手",
    "Majordomo": "总管",
    "Swift": "迅捷",
    "Alluring": "迷人",
    "Sex Specialist": "性爱专家",
    "Perfect Record": "完美记录",
    "Perfect Sub": "完美的顺从者",
    "Defying the Odds": "逆天改命",
    "Hawker": "小贩",
    "Vendor": "摊贩",
    "Merchant": "商人",
    "Twisted Desire": "扭曲的欲望",
    "Served Hot": "热腾腾上桌",
    "Sadomasochist": "施虐受虐狂",
    "Shining Reputation": "声誉卓著",
    "Social Butterfly": "交际花",
    "Unsocial Moth": "孤僻的蛾",
    "Teacher's Pet": "老师的宠儿",
    "Teacher's Nightmare": "老师的噩梦",
    "Robin the Lover": "恋人罗宾",
    "Hungry Orphan": "饥饿的孤儿",
    "Robin's Song": "罗宾的歌",
    "Whitney the Bully": "霸凌者惠特尼",
    "The Bully's Tithe": "霸凌者的贡品",
    "Delinquent Antics": "不良少年的胡闹",
    "Giddy Up": "驾！",
    "Whitney's Secret": "惠特尼的秘密",
    "Kylar the Obsessed": "痴迷的凯拉尔",
    "Not for Rats": "老鼠勿近",
    "Eden the Lonely": "孤独的伊甸",
    "Sweet and Tender": "甜蜜温柔",
    "Avery the Moneybags": "富婆艾弗里",
    "Kept": "被包养",
    "What Goes Around": "因果循环",
    "Most Exclusive": "最尊贵",
    "Pride Cometh": "傲慢必败",
    "Haute Cuisine": "高级料理",
    "Leighton the Shady": "可疑的莱顿",
    "Alex the Robust": "健壮的亚历克斯",
    "Home Cooking": "家常菜",
    "Great Hawk the Terror": "恐怖的巨鹰",
    "Return the Favour": "报答恩情",
    "Feather Trick": "羽毛戏法",
    "Wren the Sly": "狡猾的雷恩",
    "Black Wolf the Alpha": "头狼黑狼",
    "Encroaching Civilisation": "文明的侵蚀",
    "Sydney the Pure-Hearted": "纯洁的西德尼",
    "Communion": "圣餐",
    "Harper the Hypnotist": "催眠师哈珀",
    "Morgan the Lost": "迷失的摩根",
    "Gwylan the Bewitching": "迷人的格威兰",
    "Coven Comforts": "女巫团的慰藉",
    "Love Triangles": "三角恋",
    "Love Trapezoids": "梯形恋",
    "Be My Valentine": "做我的情人",
    "Ballroom Show-off": "舞厅炫耀",
    "Under the Table": "桌下交易",
    "Pub Crawl Victors": "酒吧巡游冠军",
    "Mason's Secret": "梅森的秘密",
    "Mason's Shame": "梅森的耻辱",
    "Animal Tender": "动物饲养员",
    "I Spy": "我看见了",
    "First Kiss": "初吻",
    "A Crime Most Foul": "罪大恶极",
    "Longing": "渴望",
    "Pagan Rite": "异教仪式",
    "Warmest Winter": "最温暖的冬天",
    "Trials of Faith": "信念的考验",
    "First Verse": "第一段",
    "Wildsong": "野性之歌",
    "Foxbane": "狐狸克星",
    "Purrfect": "完美喵",
    "Howl at the Moon": "对月长嚎",
    "Mess With the Bull...": "别惹公牛……",
    "Fly Like an Eagle": "如鹰翱翔",
    "You Sly Fox": "狡猾的狐狸",
    "Walk Like an Angel": "如天使般行走",
    "Falling, Falling, Falling...": "坠落、坠落、坠落……",
    "Devilish Looks": "恶魔般的美貌",
    "A Special Trait": "特殊特质",
    "A Special Trait Collector": "特殊特质收藏家",
    "Broodmother Host": "孵卵宿主",
    "Top Broodmother Host": "顶级孵卵宿主",
    "Broodmother Zoologist": "孵卵动物学家",
    "Miracle of Life": "生命的奇迹",
    "First Fatherhood": "初次为父",
    "Hail Mary": "万福玛利亚",
    "Bicycle Mother": "脚踏车母亲",
    "Life Comes in Threes": "三生有幸",
    "Life begins when you least expect": "生命总在意想不到时开始",
    "Diversity of Life": "生命的多样性",
    "Broken Dam": "决堤",
    "Seed Spreader": "播种者",
    "Producer of Lewd Fluids": "淫液制造者",
    "Literally Buckets": "真是成桶的",
    "Feeling Full": "饱胀感",
    "Head Chef": "主厨",
    "Locked In Gold": "锁在黄金中",
    "Bailey's Trouble Maker": "贝利的麻烦精",
    "Leighton's Nightmare": "莱顿的噩梦",
    "Alex's Partner": "亚历克斯的伙伴",
    "Harper's Bane": "哈珀的克星",
    "Laughingstock": "笑柄",
    "You're the Laughingstock": "你成了笑柄",
    "The Endless Deep": "无尽深渊",
    "Wet and Ruined": "湿透毁坏",
    "Terror's Equal": "与恐怖匹敌",
    "Birds of a Feather...": "物以类聚……",
    "Head of the Pack": "群狼之首",
    "Top of the Food Chain": "食物链顶端",
    "Illicit Science": "非法科学",
    "Mouth Sealed Shut": "封口",
    "Neck Deep": "深陷其中",
    "Seedy": "破败",
    "Breedy": "多产",
    "Wet Rod": "湿钓竿",
    "Master Baiter": "钓鱼大师",
    "Nice Bass": "好鲈鱼",
    "Pride of the Farm": "农场的骄傲",
    "Dawn to Dusk": "从黎明到黄昏",
    "Runaway Cattle": "逃跑的牛群",
    "Equine Rescue": "救马",
    "A Thunderous Response": "雷霆般的回应",
    "A Lewd Adventure": "淫荡的冒险",
    "Sour Dealing": "酸涩的交易",
    "Rear Passenger": "后座乘客",
    "Cornered Rogue": "被逼入绝境的流氓",
    "Pain Rider": "痛苦骑手",
    "Submerged": "沉没",
    "Farm Protector": "农场守护者",
    "A Knot to Remember": "难忘的结",
    "Wrong Size": "尺寸不对",
    "Idle Hands": "闲不下手",
    "Stolen Technology": "偷来的技术",
    "Spelunking": "洞穴探险",
    "X Marks the Spot": "X 标记处",
    "Buried Treasure": "埋藏的宝藏",
    "Abnormal Mollusc": "异常软体动物",
    "Leverage": "筹码",
    "Flurry": "风雪",
    "Under the Ice": "冰下",
    "A Festive Home": "温馨的家",
    "In Red Light": "红光之下",
    "Oh Bother": "哎呀",
    "Employee Benefits": "员工福利",
    "Not Like the Movies": "不像电影",
    "Slippery": "滑溜",
    "High Reflection": "高处倒影",
    "Schism": "分裂",
    "Catch the Wind": "追风",
    "Trading Dignity": "交换尊严",
    "Playing with Fire": "玩火",
    "Firestarter": "纵火者",
    "Dealing": "交易",
    "To Watch the Fields": "守望田野",
    "Reliable Employer": "可靠的雇主",
    "Into the Sunset": "走向夕阳",
    "Bent Copper": "贪腐警察",
    "Social Contract": "社会契约",
    "Institutionalised": "被体制化",
    "Breaker": "打破者",
    "Time and Pressure": "时间与压力",
    "More than a Number": "不只是一个数字",
    "Friends in the Sky": "天空中的朋友",
    "Not Meant to be Caged": "不该被关在笼中",
    "Slip Through the Backdoor": "从后门溜走",
    "Life of the Party": "派对灵魂",
    "Belle of the Ball": "舞会之花",
    "Breaking the Stone": "击碎石头",
    "Pound Alpha": "磅级头领",
    "Pound Runt": "磅级矮子",
    "Pounded Pound": "被猛操的磅",
    "Pound Liberator": "磅级解放者",
    "The Value of Pain": "痛苦的价值",
    "Free Booze": "免费酒水",
    "Bewitching Echoes": "迷人的回声",
    "Dark Delvings": "黑暗深掘",
    "Lurker Beyond": "彼岸潜伏者",
    "Down Below": "地底之下",
    "Bridging the Past": "连接过去",
    "Safe Trail": "安全小径",
    "Field Work": "野外作业",
    "Concrete Woodland": "混凝土林地",
    "School Green": "校园绿地",
    "Hookah Master": "水烟大师",
    "Sins of the Past": "往昔之罪",
    "Panic Room": "恐慌室",
    "Lost World": "失落的世界",
    "Prehistoric Landscape": "史前景观",
    "Face of a Guardian": "守护者之面",
    "Wild Monarch": "荒野君主",
    "Naturalised": "归化",
    "Gilded Spear": "镀金长矛",
    "Defy the Night": "挑战黑夜",
    "Withering Truth": "令人枯萎的真相",
    "Lost Heirloom": "失落的传家宝",
    "Backroom Deals": "幕后交易",
    "Stomping Down The Street": "跺脚走街头",
    "Record Keeper": "记录保管者",
    "Bramble Tamer": "荆棘驯服者",
    "Eyes in the Night": "夜中之眼",
    "Mirror Madness": "镜中疯狂",
    "Hear Me Roar": "听我怒吼",
    "Max Those Shots": "满贯射击",
    "Opened Pandora's Box": "打开了潘多拉魔盒",
    "Opened Pandora's Cocks": "打开了潘多拉的肉棒",
    "Brothel Provider": "妓院供货商",
    "Player of the Match": "全场最佳",
    "Ear Slime Lover": "耳中史莱姆爱好者",
    "Ear Slime Amalgam": "耳中史莱姆融合体",
    "The Path to Redemption": "救赎之路",
    "A New Life": "新生活",
    "Negotiator": "谈判专家",
    "Curious Attire": "古怪装束",
    "Wicked Wardrobe": "邪恶衣柜",
    "My Collection of Feats": "我的成就收藏",
    "My Timeless Collection of Feats": "我的永恒成就收藏",
}

# 定位 setup.feats = { ... } 块
m = re.search(r"setup\.feats\s*=\s*\{", data)
if not m:
    print("[AC06] 找不到 setup.feats")
    sys.exit(1)

i = m.end()
depth = 1
while i < len(data) and depth > 0:
    if data[i] == "{":
        depth += 1
    elif data[i] == "}":
        depth -= 1
    i += 1
block = data[m.start():i]
print(f"setup.feats 块长度: {len(block)}")

total = 0
for en, cn in MAP.items():
    # title: "英文"  →  title: "中文"
    old = 'title: "' + en + '"'
    new = 'title: "' + cn + '"'
    c = block.count(old)
    if c:
        block = block.replace(old, new)
        total += c
    else:
        # 试转义形态（' 变成 \'）
        if "'" in en:
            e2 = en.replace("'", "\\'")
            old2 = 'title: "' + e2 + '"'
            c2 = block.count(old2)
            if c2:
                block = block.replace(old2, new)
                total += c2

data = data[:m.start()] + block + data[i:]
print(f"共替换 {total} / {len(MAP)} 个")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [AC06] 成就名翻译 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m2 = re.search(r"setup\.feats\s*=\s*\{", g)
i2 = m2.end()
d2 = 1
while i2 < len(g) and d2 > 0:
    if g[i2] == "{":
        d2 += 1
    elif g[i2] == "}":
        d2 -= 1
    i2 += 1
blk2 = g[m2.start():i2]

titles = re.findall(r'title:\s*"((?:[^"\\]|\\.)*)"', blk2)
cn_n = sum(1 for t in titles if re.search(r"[\u4e00-\u9fff]", t))
print(f"\n校验: title 共 {len(titles)} 个，其中中文 {cn_n} 个，英文 {len(titles) - cn_n} 个")

left = [t for t in titles if not re.search(r"[\u4e00-\u9fff]", t)]
if left:
    print(f"  未翻 {len(left)} 个:")
    for t in left[:10]:
        print(f"    {t!r}")

print(f"\npassage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if cn_n == len(titles) else 1)
