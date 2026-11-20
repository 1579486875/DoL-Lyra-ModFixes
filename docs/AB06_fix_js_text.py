"""AB06：翻译玩家可见的 JS 硬编码英文（第一批：性商店 / 森林商店 / 颜色 / 身体变化）。

保留不翻的（玩家看不到）：
  - 温度/天气面板（在 ${V.debug ? ...} 里）
  - DEBUG OPTIONS / ERROR: xxx / NPCINCR error
  - /* */ 注释里的
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AB06] index 形态异常")
    sys.exit(1)

MARK = "[AB06]"
g0 = H.unescape(data)
if MARK in g0:
    print("[AB06] 已存在，跳过")
    sys.exit(0)

# 用「带标签的完整串」做精确替换（避免误伤）
FIXES = [
    # ===== 性商店 =====
    ('<span class="ssm_not_enough_money">Not enough money</span>',
     '<span class="ssm_not_enough_money">钱不够</span>'),
    ('class="ssm_buy_button">Buy it</a>',
     'class="ssm_buy_button">买下</a>'),
    ('<span style="color: #e0e0e0">Colours to choose from: </span>',
     '<span style="color: #e0e0e0">可选颜色：</span>'),
    # ===== 自定义颜色 =====
    ('<span class="export-custom-colour-alert">Copied to clipboard!</span>',
     '<span class="export-custom-colour-alert">已复制到剪贴板！</span>'),
    ('<span class="export-custom-colour-error">Invalid code.</span>',
     '<span class="export-custom-colour-error">代码无效。</span>'),
    # ===== 森林商店解锁通知 =====
    ('<span class="orange">Halloween clothes</span> <span class="gold">are now available at the forest shop!</span>',
     '<span class="orange">万圣节服装</span><span class="gold">现已在森林商店上架！</span>'),
    ('<span class="green">Christmas clothes</span> <span class="gold">are now available at the forest shop!</span>',
     '<span class="green">圣诞服装</span><span class="gold">现已在森林商店上架！</span>'),
    ('<span class="brown">Feathered accessories</span> <span class="gold">are now available at the forest shop!</span>',
     '<span class="brown">羽毛配饰</span><span class="gold">现已在森林商店上架！</span>'),
    ('<span class="gold">New clothes are available at the forest shop:</span>',
     '<span class="gold">森林商店上新：</span>'),
    # ===== 森林商店天气描述 =====
    ("<span class='blue'>It's extremely cold outside.</span>",
     "<span class='blue'>外面冷得刺骨。</span>"),
    ("<span class='purple'>It's very cold outside.</span>",
     "<span class='purple'>外面非常冷。</span>"),
    ("<span class='teal'>It's cold outside.</span>",
     "<span class='teal'>外面有点冷。</span>"),
    ("<span class='green'>It's a comfortable temperature outside.</span>",
     "<span class='green'>外面的温度很舒适。</span>"),
    ("<span class='orange'>It's hot outside.</span>",
     "<span class='orange'>外面很热。</span>"),
    # ===== 身体变化描述 =====
    ('"Horns sprout from your scalp."', '"你的头皮上冒出了犄角。"'),
    ('"A tail sprouts from your lower back."', '"你的后腰长出了一条尾巴。"'),
    ('"A new chastity parasite forms around your penis."', '"一个全新的贞操寄生虫在你肉棒周围成形。"'),
    ('"Her pussy hovers above you."', '"她的小穴悬在你上方。"'),
    ('"His pussy hovers above you."', '"他的小穴悬在你上方。"'),
    ('"Its pussy hovers above you."', '"它的小穴悬在你上方。"'),
    ('"It continues to force you to play with yourself."', '"它继续逼迫你玩弄自己。"'),
    ('"It creaks in protest. One more kick will do it."', '"它嘎吱作响地抗议。再踹一脚就行了。"'),
    ('"It tastes very strange"', '"味道非常古怪"'),
    ('"A dull click is the only result."', '"只传来一声沉闷的咔哒。"'),
    ('"A set of antique chainmail"', '"一套古董锁子甲"'),
]

total = 0
print("=" * 90)
print("翻译（第一批）")
print("=" * 90)
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {old[:62]!r}")
    else:
        print(f"  MISS     {old[:62]!r}")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [AB06] JS 硬编码英文第一批 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
BAD = ["Not enough money", "Buy it</a>", "Colours to choose from",
       "Copied to clipboard!", "Invalid code."]
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
for b in BAD:
    n = g.count(b)
    print(f"  {'OK ' if n == 0 else 'FAIL'} {b!r}: {n}")
print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if total >= 20 else 1)
