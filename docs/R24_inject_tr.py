"""第 24 轮：翻译并注入 19 条真漏翻。

按模板要求（信达雅 + 贴合语境 + 保留特殊标记）。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

PAIRS = [
    ("It exits with a pop, prompting Gwylan to slowly moan.",
     "它「啵」地一声抽了出来，引得格威岚缓缓呻吟起来。"),
    ("You're free to explore the building during the day.",
     "白天你可以自由探索这栋建筑。"),
    ("Don't enter any doors marked for staff, and make sure to follow instructions.",
     "别进入任何标有「员工专用」的门，并且务必遵从指示。"),
    ("They turn to regard you.",
     "他们转过身来打量你。"),
    ("You've been displaying your body in inappropriate ways, then claiming others stripped you.",
     "你一直以不当的方式展示自己的身体，事后却声称是别人剥光了你的衣服。"),
    ("You both stop for a moment.",
     "你们都停下了片刻。"),
    ("Its wooden face is the last thing you see as the gloom envelops you.",
     "当阴霾将你吞没时，你最后看到的是它那张木制的脸。"),
    ("Smart thinking, with the light.",
     "还知道带着灯，挺机灵。"),
    ("You open your eyes to see the Black Wolf curling up beside you.",
     "你睁开眼，看见黑狼正蜷缩在你身旁。"),
    ("The Black Wolf drops some by your side before moving away.",
     "黑狼把一些东西放在了你的身旁，然后走开了。"),
    ("A single white light turns on above you, and the din of the dark room falls quiet.",
     "一盏白灯在你头顶亮起，昏暗房间里的喧闹顿时安静下来。"),
    ("You can't see beyond the edge of the stage, but you can feel the eyes on you.",
     "你看不清舞台边缘之外的地方，却能感觉到无数目光落在你身上。"),
    ("Paper flies everywhere as both of you tumble to the ground.",
     "你们两人一起跌倒在地，纸张四处飞散。"),
    ("Your heart continues to beat rapidly.",
     "你的心脏仍在剧烈跳动。"),
    ("You hear a whistle blow behind you.",
     "你听到身后传来一声哨响。"),
    ("You hear a tear.",
     "你听到一声撕裂声。"),
    ("It's a look you've seen before.",
     "那是你曾经见过的眼神。"),
    ("The key to the belt is long lost.",
     "贞操带的钥匙早已不知所踪。"),
]

# 特殊处理：带引号的
QUOTED = [
    ('"Everything will be fine," you say.',
     "“一切都会好起来的，”你说。"),
]

data = open(HTML, "rb").read().decode("utf-8", "replace")
total = 0
report = []

for en, cn in PAIRS + QUOTED:
    hit = 0
    for a, b in ((H.escape(en, quote=False), H.escape(cn, quote=False)),
                 (en, cn)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            hit += n
            break
    total += hit
    report.append((en, cn, hit))
    print(f"  {'✅' if hit else '⚠️'} {hit:>2} 处  {en[:60]!r}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n共替换 {total} 处，已写回 {HTML}")
else:
    print("\n（无替换）")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
rem = 0
for en, cn in PAIRS + QUOTED:
    n = g.count(en)
    if n:
        rem += n
        print(f"  ⚠️ 残留 {n}: {en[:50]!r}")
print(f"  英文残留总数: {rem}")

# 检查中文是否都在
ok = 0
for en, cn in PAIRS + QUOTED:
    if cn in g:
        ok += 1
print(f"  中文已注入: {ok}/{len(PAIRS)+len(QUOTED)}")

sys.exit(0 if rem == 0 else 1)
