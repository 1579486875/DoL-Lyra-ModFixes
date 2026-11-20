"""U08：修「裸英文副词」61 处（用前置锚点精确匹配，避免短词误伤）。

这些都是 <<if>> 分支里直接输出给玩家的英文：
  动作副词 fencing/pressing/slithers/twitches/trembles/slithering/twitching/remove
  兽化类型 wolf/cat/cow/harpy/fox/girl/girls
  肤色     dark/medium/light
  NPC名    Alex's Hardy Dad / Whitney's Uncle ...
  礼仪     bow/Bow
  语法词   are/is/and/their
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[U08] index 形态异常")
    sys.exit(1)

MARK = "[U08]"
g0 = H.unescape(data)
if MARK in g0:
    print("[U08] 已存在，跳过")
    sys.exit(0)

# (前置锚点, 英文, 中文) —— 前置锚点保证唯一性
FIXES = [
    # ---- 动作副词 ----
    ('<<if $enemyarousal gte (($enemyarousalmax / 10) * 7)>>\n\t\t\t\t\tfencing\n',
     '<<if $enemyarousal gte (($enemyarousalmax / 10) * 7)>>\n\t\t\t\t\t击剑式地\n'),
    ('<<else>>\n\t\t\t\t\tpressing\n',
     '<<else>>\n\t\t\t\t\t挤压着\n'),
    ('<<else>>\n\t\t\t\tpressing\n\t\t\t<</if>>',
     '<<else>>\n\t\t\t\t挤压着\n\t\t\t<</if>>'),
    ('<<if $rng gte 96>>\n\t\tslithers\n', '<<if $rng gte 96>>\n\t\t滑行\n'),
    ('<<if $rng gte 96>>\n\t\tslithering\n', '<<if $rng gte 96>>\n\t\t滑动着\n'),
    ('<<elseif $rng gte 36>>\n\t\ttwitches\n', '<<elseif $rng gte 36>>\n\t\t抽搐\n'),
    ('<<elseif $rng gte 36>>\n\t\ttwitching\n', '<<elseif $rng gte 36>>\n\t\t抽搐着\n'),
    ('<<elseif $rng gte 31>>\n\t\tshivers\n', '<<elseif $rng gte 31>>\n\t\t颤栗\n'),
    ('<<elseif $rng gte 26>>\n\t\ttrembles\n', '<<elseif $rng gte 26>>\n\t\t颤抖\n'),
    ('<<else>>\n\t\tremove\n', '<<else>>\n\t\t脱下\n'),
    # ---- 兽化类型 ----
    ('<<elseif $wolfgirl gte 6>>\n\t\t\twolf\n', '<<elseif $wolfgirl gte 6>>\n\t\t\t狼\n'),
    ('<<elseif $cat gte 6>>\n\t\t\tcat\n', '<<elseif $cat gte 6>>\n\t\t\t猫\n'),
    ('<<else>>\n\t\t\t\tcow\n', '<<else>>\n\t\t\t\t牛\n'),
    ('<<else>>\n\t\t\t\t\t\tcow\n', '<<else>>\n\t\t\t\t\t\t牛\n'),
    ('<<if $hallucinations gte 2 or !$settings.bestialityEnabled>>\n\t\t\t\tharpy\n',
     '<<if $hallucinations gte 2 or !$settings.bestialityEnabled>>\n\t\t\t\t鹰身女妖\n'),
    ('<<elseif $fox gte 6>>\n\t\t\tfox\n', '<<elseif $fox gte 6>>\n\t\t\t狐\n'),
    ('<<else>>\n\tgirl\n<</if>>', '<<else>>\n\t女孩\n<</if>>'),
    ('<<else>>\n\t\tgirls\n\t<</if>>', '<<else>>\n\t\t女孩们\n\t<</if>>'),
    # ---- 肤色 ----
    ('<<if Skin.color.tan gte 66>>\n\t\t\tdark\n', '<<if Skin.color.tan gte 66>>\n\t\t\t深色\n'),
    ('<<elseif Skin.color.tan gte 33>>\n\t\t\tmedium\n', '<<elseif Skin.color.tan gte 33>>\n\t\t\t中等\n'),
    ('<<else>>\n\t\t\tlight\n\t\t<</if>>\n\t\t的皮肤。', '<<else>>\n\t\t\t浅色\n\t\t<</if>>\n\t\t的皮肤。'),
    # ---- NPC 名 ----
    ("Alex's Hardy Dad", "亚历克斯健壮的父亲"),
    ("Alex's Hardy Mum", "亚历克斯健壮的母亲"),
    ("Alex's Calculating Dad", "亚历克斯精于算计的父亲"),
    ("Alex's Calculating Mum", "亚历克斯精于算计的母亲"),
    ("Whitney's Uncle", "惠特尼的叔叔"),
    ("Whitney's Aunt", "惠特尼的姑妈"),
    ("Whitney's Dad", "惠特尼的父亲"),
    ("Whitney's Mum", "惠特尼的母亲"),
]

total = 0
print("=" * 90)
print("修复")
print("=" * 90)
for item in FIXES:
    if len(item) == 2:
        old, new = item
    else:
        anchor, en, cn = item
        old, new = anchor, anchor.replace(en, cn)

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
        print(f"  MISS     {old[:60]!r}")

# ---- 语法词（单独处理，因为要保证结构）----
print("\n" + "=" * 90)
print("语法词（are / is / and / their）")
print("=" * 90)
GRAMMAR = [
    # their
    ('<<if _args[0] is "two">>\n\t\ttheir\n', '<<if _args[0] is "two">>\n\t\t他们的\n'),
    ('<<elseif $enemyno gte 2 and $enemytype is "man">>\n\t\ttheir\n',
     '<<elseif $enemyno gte 2 and $enemytype is "man">>\n\t\t他们的\n'),
    # and（列表连接词，中文用顿号）
    ('<<if $worn.over_upper.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.upper.cn_name_cap',
     '<<if $worn.over_upper.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.upper.cn_name_cap'),
    ('<<if $worn.over_upper.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.under_upper.name',
     '<<if $worn.over_upper.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.under_upper.name'),
    ('<<if $worn.over_lower.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.lower.cn_name_cap',
     '<<if $worn.over_lower.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.lower.cn_name_cap'),
    ('<<if $worn.over_lower.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.under_lower.cn_name_cap',
     '<<if $worn.over_lower.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.under_lower.cn_name_cap'),
    # are / is（中文不需要系动词，用零宽占位保证结构）
    ('<<if $_part is "thighs" or $_part is "feet">>\n\t\t\tare\n',
     '<<if $_part is "thighs" or $_part is "feet">>\n\t\t\t\u200b\n'),
    ('<<else>>\n\t\t\tis\n\t\t<</if>>\n\t\t<<if $_semen gt 0>>',
     '<<else>>\n\t\t\t\u200b\n\t\t<</if>>\n\t\t<<if $_semen gt 0>>'),
]
for old, new in GRAMMAR:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {old[:55]!r}")
    else:
        print(f"  MISS     {old[:55]!r}")

# ---- 礼仪 bow ----
print("\n" + "=" * 90)
print("礼仪 bow / Bow")
print("=" * 90)
for old, new in (
    ('<<if $player.gender_appearance is "m">>\n\t\t\t\t\t\t\tBow\n',
     '<<if $player.gender_appearance is "m">>\n\t\t\t\t\t\t\t鞠躬\n'),
):
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x")
    else:
        print(f"  MISS  {old[:55]!r}")

# ---- speechrammalentrance ----
print("\n" + "=" * 90)
print("$speechrammalentrance -> $speechrammingentrance")
print("=" * 90)
for old, new in (("speechrammalentrance", "speechrammingentrance"),):
    hit = 0
    for a, b in ((old, new),):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x")
    else:
        print(f"  MISS")

# 打标记
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [U08] 裸英文副词清理 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 复扫 ----
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
PAT = re.compile(r"<<(if|elseif|else)\b[^>]*>>\s*\n\s*([A-Za-z][A-Za-z\- ']{1,40})\s*\n\s*<<", re.M)
left = []
for m in PAT.finditer(g):
    w = m.group(2).strip()
    if not w or re.search(r"[\u4e00-\u9fff]", w):
        continue
    if w.startswith("<<") or w.startswith("<") or re.search(r"[${}()\[\];=]", w):
        continue
    left.append(w)

print("\n" + "=" * 90)
print(f"复扫剩余: {len(left)} 处")
print("=" * 90)
from collections import Counter
for w, c in Counter(left).most_common(40):
    print(f"  {c:>3}  {w!r}")
