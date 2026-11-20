"""AB08：第二批 JS 硬编码英文（身体变化 + 性商店第二处 + alert）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AB08] index 形态异常")
    sys.exit(1)

MARK = "[AB08]"
g0 = H.unescape(data)
if MARK in g0:
    print("[AB08] 已存在，跳过")
    sys.exit(0)

# 用带标签的完整形态
FIXES = [
    # ===== 性商店：第二处 Buy it（带 fade_in_fast 类）=====
    ('class="ssm_buy_button ssm_fade_in_fast">Buy it</a>',
     'class="ssm_buy_button ssm_fade_in_fast">买下</a>'),
    # ===== alert 弹窗 =====
    ('alert("Copied to clipboard!");', 'alert("已复制到剪贴板！");'),
    # ===== 身体变化描述（带 span 标签）=====
    ('<span class="gold">Horns sprout from your scalp.</span>',
     '<span class="gold">你的头皮上冒出了犄角。</span>'),
    ('<span class="gold">A tail sprouts from your lower back.</span>',
     '<span class="gold">你的后腰长出了一条尾巴。</span>'),
    # ===== 半人马 / 马 的 pussy hovers =====
    ('<span class="purple">Her pussy hovers above you.</span>',
     '<span class="purple">她的小穴悬在你上方。</span>'),
    ('<span class="purple">His pussy hovers above you.</span>',
     '<span class="purple">他的小穴悬在你上方。</span>'),
    ('<span class="purple">Its pussy hovers above you.</span>',
     '<span class="purple">它的小穴悬在你上方。</span>'),
    # ===== 其他身体变化（先按 span 形态试，不行再说）=====
    ('<span class="gold">It continues to force you to play with yourself.</span>',
     '<span class="gold">它继续逼迫你玩弄自己。</span>'),
    ('<span class="gold">It creaks in protest. One more kick will do it.</span>',
     '<span class="gold">它嘎吱作响地抗议。再踹一脚就行了。</span>'),
    ('<span class="gold">It tastes very strange</span>',
     '<span class="gold">味道非常古怪</span>'),
    ('<span class="gold">A dull click is the only result.</span>',
     '<span class="gold">只传来一声沉闷的咔哒。</span>'),
    ('<span class="gold">A set of antique chainmail</span>',
     '<span class="gold">一套古董锁子甲</span>'),
]

# 无标签兜底（去掉 span 包裹）
FALLBACK = [
    ('"It continues to force you to play with yourself."', '"它继续逼迫你玩弄自己。"'),
    ('"It creaks in protest. One more kick will do it."', '"它嘎吱作响地抗议。再踹一脚就行了。"'),
    ('"It tastes very strange"', '"味道非常古怪"'),
    ('"A dull click is the only result."', '"只传来一声沉闷的咔哒。"'),
    ('"A set of antique chainmail"', '"一套古董锁子甲"'),
    ('"Horns sprout from your scalp."', '"你的头皮上冒出了犄角。"'),
    ('"A tail sprouts from your lower back."', '"你的后腰长出了一条尾巴。"'),
    ('"Her pussy hovers above you."', '"她的小穴悬在你上方。"'),
    ('"His pussy hovers above you."', '"他的小穴悬在你上方。"'),
    ('"Its pussy hovers above you."', '"它的悬在你上方。"'),
]

total = 0
print("=" * 90)
print("第二批（带标签形态）")
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
        print(f"  OK {hit}x  {old[:60]!r}")
    else:
        print(f"  --       {old[:60]!r}")

print("\n" + "=" * 90)
print("兜底（无标签形态）")
print("=" * 90)
for old, new in FALLBACK:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {old[:60]!r}")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [AB08] JS 硬编码英文第二批 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
BAD = [
    "Buy it</a>",
    'alert("Copied to clipboard!"',
    "Horns sprout from your scalp",
    "A tail sprouts from your lower back",
    "Her pussy hovers above you",
    "His pussy hovers above you",
    "Its pussy hovers above you",
    "It continues to force you to play with yourself",
    "It creaks in protest",
    "It tastes very strange",
    "A dull click is the only result",
    "A set of antique chainmail",
]
fail = 0
for b in BAD:
    n = g.count(b)
    if n:
        fail += 1
    print(f"  {'OK ' if n == 0 else 'FAIL'} {b!r}: {n}")

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if fail == 0 else 1)
