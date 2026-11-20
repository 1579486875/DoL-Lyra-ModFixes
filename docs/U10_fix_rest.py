"""U10：修剩余 31 处裸英文（继续用前置锚点）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[U10] index 形态异常")
    sys.exit(1)

MARK = "[U10]"
g0 = H.unescape(data)
if MARK in g0:
    print("[U10] 已存在，跳过")
    sys.exit(0)

FIXES = [
    # ---- nectar ----
    ('<<if $_thisSpecies.name is "plant">>\n\t\t\t\t\t\tnectar\n',
     '<<if $_thisSpecies.name is "plant">>\n\t\t\t\t\t\t花蜜\n'),
    ('<<if $_thisItem.name is "plant">>\n\t\t\t\t\t\tnectar\n',
     '<<if $_thisItem.name is "plant">>\n\t\t\t\t\t\t花蜜\n'),
    # ---- semen ----
    ('<<if maleChance() >= 100>>\n\t\t\t\t\t\t\tsemen\n',
     '<<if maleChance() >= 100>>\n\t\t\t\t\t\t\t精液\n'),
    ('<<elseif maleChance() gte 100>>\n\t\t\t\t\t\tsemen\n',
     '<<elseif maleChance() gte 100>>\n\t\t\t\t\t\t精液\n'),
    # ---- You（承接前一句"凭借你的..."）----
    ('<<else>>\n\t\t\t\t\tYou\n\t\t\t\t<</if>>\n\t\t\t\t捕捉到了',
     '<<else>>\n\t\t\t\t\t\u200b\n\t\t\t\t<</if>>\n\t\t\t\t捕捉到了'),
    # ---- an / a（英文冠词，中文用零宽占位）----
    ('<<if setup.clothes[_random_slot][_random_index].word is "an">>\n\t\t\t\tan\n\t\t\t<<else>>\n\t\t\t\ta\n',
     '<<if setup.clothes[_random_slot][_random_index].word is "an">>\n\t\t\t\t\u200b\n\t\t\t<<else>>\n\t\t\t\t\u200b\n'),
    # ---- it ----
    ('<<if setup.clothes[_random_slot][_random_index].plural isnot 1>>\n\t\t\tit\n',
     '<<if setup.clothes[_random_slot][_random_index].plural isnot 1>>\n\t\t\t它\n'),
    # ---- pussy ×6 ----
    ('<<else>>\n\tpussy\n<</if>>\n。\n<br><br>\n\n“我不会再对你手软了，”',
     '<<else>>\n\t小穴\n<</if>>\n。\n<br><br>\n\n“我不会再对你手软了，”'),
    ('<<else>>\n\t\tpussy\n\t<</if>>\n\t消失了。',
     '<<else>>\n\t\t小穴\n\t<</if>>\n\t消失了。'),
    ('<<if $player.penisExist>>\n\t\t<<penis>>\n\t<<else>>\n\t\tpussy\n\t<</if>>\n\t片刻，然后',
     '<<if $player.penisExist>>\n\t\t<<penis>>\n\t<<else>>\n\t\t小穴\n\t<</if>>\n\t片刻，然后'),
    # ---- chest ×2 ----
    ('<<if $NPCList[0].breastsize is 0>>\n\t\t\t\t\t\tchest\n',
     '<<if $NPCList[0].breastsize is 0>>\n\t\t\t\t\t\t胸部\n'),
    # ---- my ----
    ('<<if C.npc.Alex.dom gte 20>>\n\t\tmy\n',
     '<<if C.npc.Alex.dom gte 20>>\n\t\t我的\n'),
    # ---- man / woman ×3 ----
    ('<<if $NPCList[0].gender is "m">>\n\t\t\t\tman\n\t\t\t<<else>>\n\t\t\t\twoman\n',
     '<<if $NPCList[0].gender is "m">>\n\t\t\t\t男人\n\t\t\t<<else>>\n\t\t\t\t女人\n'),
    # ---- brittle ----
    ('<<elseif $trauma gte (($traumamax / 5) * 1)>>\n\t\t\tbrittle\n',
     '<<elseif $trauma gte (($traumamax / 5) * 1)>>\n\t\t\t脆弱的\n'),
    # ---- meek ----
    ('<<if C.npc.Robin.dom lte 40>>\n\t\tmeek\n',
     '<<if C.npc.Robin.dom lte 40>>\n\t\t怯懦的\n'),
    # ---- women ×2 ----
    ('<<elseif $settings.maleVictimChance lte 0>>\n\twomen\n<<else>>\n\t男人和女人的\n<</if>>\n的照片贴满了',
     '<<elseif $settings.maleVictimChance lte 0>>\n\t女人们的\n<<else>>\n\t男人和女人的\n<</if>>\n的照片贴满了'),
    ('<<elseif $settings.maleVictimChance lte 0>>\n\t\twomen\n\t<<else>>\n\t\t男人和女人的\n\t<</if>>\n\t照片贴满了',
     '<<elseif $settings.maleVictimChance lte 0>>\n\t\t女人们的\n\t<<else>>\n\t\t男人和女人的\n\t<</if>>\n\t照片贴满了'),
    # ---- silently ----
    ('<<elseif $player.penisExist>>\n\t\tsilently\n',
     '<<elseif $player.penisExist>>\n\t\t无声地\n'),
]

total = 0
print("=" * 90)
print("修复")
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
        print(f"  OK {hit}x  {old[:58]!r}")
    else:
        print(f"  MISS     {old[:58]!r}")

# 打标记
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [U10] 裸英文清理第二批 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# 复扫
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
for w, c in Counter(left).most_common(30):
    print(f"  {c:>3}  {w!r}")
