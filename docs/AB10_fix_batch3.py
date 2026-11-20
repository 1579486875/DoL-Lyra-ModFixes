"""AB10：第三批 JS 硬编码英文（各种 span 颜色 + 新发现的 continues kicking）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AB10] index 形态异常")
    sys.exit(1)

MARK = "[AB10]"
g0 = H.unescape(data)
if MARK in g0:
    print("[AB10] 已存在，跳过")
    sys.exit(0)

FIXES = [
    # ===== 触手/寄生虫：两条（带 red span，单引号转义）=====
    ("<span class=\\'red\\'>It continues to force you to play with yourself, but limits its control so you can do your task.</span>",
     "<span class=\\'red\\'>它继续逼迫你玩弄自己，但限制了控制力，好让你完成任务。</span>"),
    ("<span class=\\'red\\'>It continues to force you to play with yourself.</span>",
     "<span class=\\'red\\'>它继续逼迫你玩弄自己。</span>"),
    # 未转义形态兜底
    ('<span class="red">It continues to force you to play with yourself, but limits its control so you can do your task.</span>',
     '<span class="red">它继续逼迫你玩弄自己，但限制了控制力，好让你完成任务。</span>'),
    ('<span class="red">It continues to force you to play with yourself.</span>',
     '<span class="red">它继续逼迫你玩弄自己。</span>'),
    # ===== 踹门 =====
    ('<span class="blue">It creaks in protest. One more kick will do it.</span>',
     '<span class="blue">它嘎吱作响地抗议。再踹一脚就行了。</span>'),
    (' continues kicking the door.', ' 继续踹门。'),
    # ===== 植物味道 =====
    ('<span class="red">It tastes very strange</span>',
     '<span class="red">味道非常古怪</span>'),
    # ===== 开枪哑火 =====
    ('<span class="blue">A dull click is the only result.</span>',
     '<span class="blue">只传来一声沉闷的咔哒。</span>'),
    # ===== 古董锁子甲 =====
    ('<span class="grey">A set of antique chainmail</span>',
     '<span class="grey">一套古董锁子甲</span>'),
]

total = 0
print("=" * 90)
print("第三批")
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
        print(f"  OK {hit}x  {old[:65]!r}")
    else:
        print(f"  --       {old[:65]!r}")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [AB10] JS 硬编码英文第三批 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
BAD = [
    "It continues to force you to play with yourself",
    "It creaks in protest",
    "continues kicking the door.",
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
