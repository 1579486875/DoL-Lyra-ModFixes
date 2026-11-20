"""AB13：翻译玩家可见的 JS 硬编码英文（幂等）。

保留不翻（玩家看不到）：
  - 温度/天气面板（在 ${V.debug ? ...} 里）
  - DEBUG OPTIONS / ERROR: xxx / NPCINCR error
  - /* */ 注释里的

策略：用「纯文本片段」做锚点，避免标签/转义的层级问题。
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AB13] index 形态异常")
    sys.exit(1)

MARK = "[AB13]"
g0 = H.unescape(data)
if MARK in g0:
    print("[AB13] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

# (纯文本锚点, 中文) —— 顺序很重要：长串必须排在短串前面
FIXES = [
    # ===== 触手/寄生虫（必须先长后短）=====
    ("It continues to force you to play with yourself, but limits its control so you can do your task.",
     "它继续逼迫你玩弄自己，但限制了控制力，好让你完成任务。"),
    ("It continues to force you to play with yourself.",
     "它继续逼迫你玩弄自己。"),
    # ===== 性商店 =====
    ("Not enough money", "钱不够"),
    ("Buy it", "买下"),
    ("Colours to choose from: ", "可选颜色："),
    # ===== 自定义颜色 =====
    ("Copied to clipboard!", "已复制到剪贴板！"),
    ("Invalid code.", "代码无效。"),
    # ===== 森林商店解锁通知 =====
    ("Halloween clothes", "万圣节服装"),
    ("Christmas clothes", "圣诞服装"),
    ("Feathered accessories", "羽毛配饰"),
    ("New clothes are available at the forest shop:", "森林商店上新："),
    ("are now available at the forest shop!", "现已在森林商店上架！"),
    ("is now available at the forest shop!", "现已在森林商店上架！"),
    ("A set of antique chainmail", "一套古董锁子甲"),
    # ===== 森林商店天气 =====
    ("It's extremely cold outside.", "外面冷得刺骨。"),
    ("It's very cold outside.", "外面非常冷。"),
    ("It's a comfortable temperature outside.", "外面的温度很舒适。"),
    ("It's cold outside.", "外面有点冷。"),
    ("It's hot outside.", "外面很热。"),
    # ===== 身体变化 =====
    ("Horns sprout from your scalp.", "你的头皮上冒出了犄角。"),
    ("A tail sprouts from your lower back.", "你的后腰长出了一条尾巴。"),
    ("A new chastity parasite forms around your penis.", "一个全新的贞操寄生虫在你肉棒周围成形。"),
    ("Her pussy hovers above you.", "她的小穴悬在你上方。"),
    ("His pussy hovers above you.", "他的小穴悬在你上方。"),
    ("Its pussy hovers above you.", "它的小穴悬在你上方。"),
    # ===== 其他 =====
    ("It creaks in protest. One more kick will do it.", "它嘎吱作响地抗议。再踹一脚就行了。"),
    (" continues kicking the door.", " 继续踹门。"),
    ("It tastes very strange", "味道非常古怪"),
    ("A dull click is the only result.", "只传来一声沉闷的咔哒。"),
]

total = 0
for old, new in FIXES:
    c = data.count(old)
    if c:
        data = data.replace(old, new)
        total += c

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [AB13] JS 硬编码英文 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# 校验（只查「明确该消失」的）
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
BAD = [
    "It continues to force you to play with yourself",
    "Not enough money",
    "Colours to choose from",
    "Copied to clipboard!",
    "Invalid code.",
    "Horns sprout from your scalp",
    "A tail sprouts from your lower back",
    "Her pussy hovers above you",
    "His pussy hovers above you",
    "Its pussy hovers above you",
    "It creaks in protest",
    "continues kicking the door.",
    "It tastes very strange",
    "A dull click is the only result",
    "A set of antique chainmail",
]
bad_n = sum(1 for b in BAD if g.count(b) > 0)
ok = bad_n == 0
print("[AB13] 修 %d 处  残留项=%d  passage=%d  %s" % (
    total, bad_n,
    len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
if bad_n:
    for b in BAD:
        if g.count(b):
            print("   FAIL:", repr(b), g.count(b))
sys.exit(0 if ok else 1)
