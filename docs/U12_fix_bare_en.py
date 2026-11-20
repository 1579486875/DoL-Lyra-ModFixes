"""U12：清除「裸英文副词」—— <<if>> 分支里直接输出的英文单词（幂等）。

这类文本 i18n 完全扫不到（不是字符串、不是宏参数），但会原样显示给玩家：
  fencing / pressing / slithers / twitches / trembles / shivering ...
  wolf / cat / cow / harpy / fox / girl / girls
  dark / medium / light
  Alex's Hardy Dad / Whitney's Uncle ...
  bow / Filters / Help / pussy / man / woman / chest / nectar / brittle / meek / silently
  are / is / and / their / The / You / it / my / an
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[U12] index 形态异常")
    sys.exit(1)

MARK = "[U12]"
g0 = H.unescape(data)
if MARK in g0:
    print("[U12] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

Z = "\u200b"   # 零宽空格：替代英文冠词/系动词，保持结构不产生空白行

FIXES = [
    # ===== 动作副词 =====
    ('<<if $enemyarousal gte (($enemyarousalmax / 10) * 7)>>\n\t\t\t\t\tfencing\n',
     '<<if $enemyarousal gte (($enemyarousalmax / 10) * 7)>>\n\t\t\t\t\t击剑式地\n'),
    ('<<else>>\n\t\t\t\t\tpressing\n', '<<else>>\n\t\t\t\t\t挤压着\n'),
    ('<<else>>\n\t\t\t\tpressing\n\t\t\t<</if>>', '<<else>>\n\t\t\t\t挤压着\n\t\t\t<</if>>'),
    ('<<if $rng gte 96>>\n\t\tslithers\n', '<<if $rng gte 96>>\n\t\t滑行\n'),
    ('<<if $rng gte 96>>\n\t\tslithering\n', '<<if $rng gte 96>>\n\t\t滑动着\n'),
    ('<<elseif $rng gte 36>>\n\t\ttwitches\n', '<<elseif $rng gte 36>>\n\t\t抽搐\n'),
    ('<<elseif $rng gte 36>>\n\t\ttwitching\n', '<<elseif $rng gte 36>>\n\t\t抽搐着\n'),
    ('<<elseif $rng gte 31>>\n\t\tshivers\n', '<<elseif $rng gte 31>>\n\t\t颤栗\n'),
    ('<<elseif $rng gte 26>>\n\t\ttrembles\n', '<<elseif $rng gte 26>>\n\t\t颤抖\n'),
    ('<<else>>\n\t\tremove\n', '<<else>>\n\t\t脱下\n'),
    # ===== 兽化类型 =====
    ('<<elseif $wolfgirl gte 6>>\n\t\t\twolf\n', '<<elseif $wolfgirl gte 6>>\n\t\t\t狼\n'),
    ('<<elseif $cat gte 6>>\n\t\t\tcat\n', '<<elseif $cat gte 6>>\n\t\t\t猫\n'),
    ('<<else>>\n\t\t\t\tcow\n', '<<else>>\n\t\t\t\t牛\n'),
    ('<<else>>\n\t\t\t\t\t\tcow\n', '<<else>>\n\t\t\t\t\t\t牛\n'),
    ('<<if $hallucinations gte 2 or !$settings.bestialityEnabled>>\n\t\t\t\tharpy\n',
     '<<if $hallucinations gte 2 or !$settings.bestialityEnabled>>\n\t\t\t\t鹰身女妖\n'),
    ('<<elseif $fox gte 6>>\n\t\t\tfox\n', '<<elseif $fox gte 6>>\n\t\t\t狐\n'),
    ('<<else>>\n\tgirl\n<</if>>', '<<else>>\n\t女孩\n<</if>>'),
    ('<<else>>\n\t\tgirls\n\t<</if>>', '<<else>>\n\t\t女孩们\n\t<</if>>'),
    # ===== 肤色 =====
    ('<<if Skin.color.tan gte 66>>\n\t\t\tdark\n', '<<if Skin.color.tan gte 66>>\n\t\t\t深色\n'),
    ('<<elseif Skin.color.tan gte 33>>\n\t\t\tmedium\n', '<<elseif Skin.color.tan gte 33>>\n\t\t\t中等\n'),
    ('<<else>>\n\t\t\tlight\n\t\t<</if>>\n\t\t的皮肤。', '<<else>>\n\t\t\t浅色\n\t\t<</if>>\n\t\t的皮肤。'),
    # ===== NPC 名 =====
    ("Alex's Hardy Dad", "亚历克斯健壮的父亲"),
    ("Alex's Hardy Mum", "亚历克斯健壮的母亲"),
    ("Alex's Calculating Dad", "亚历克斯精于算计的父亲"),
    ("Alex's Calculating Mum", "亚历克斯精于算计的母亲"),
    ("Whitney's Uncle", "惠特尼的叔叔"),
    ("Whitney's Aunt", "惠特尼的姑妈"),
    ("Whitney's Dad", "惠特尼的父亲"),
    ("Whitney's Mum", "惠特尼的母亲"),
    # ===== 语法词 =====
    ('<<if _args[0] is "two">>\n\t\ttheir\n', '<<if _args[0] is "two">>\n\t\t他们的\n'),
    ('<<elseif $enemyno gte 2 and $enemytype is "man">>\n\t\ttheir\n',
     '<<elseif $enemyno gte 2 and $enemytype is "man">>\n\t\t他们的\n'),
    ('<<if $worn.over_upper.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.upper.cn_name_cap',
     '<<if $worn.over_upper.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.upper.cn_name_cap'),
    ('<<if $worn.over_upper.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.under_upper.name',
     '<<if $worn.over_upper.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.under_upper.name'),
    ('<<if $worn.over_lower.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.lower.cn_name_cap',
     '<<if $worn.over_lower.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.lower.cn_name_cap'),
    ('<<if $worn.over_lower.name isnot "naked">>\n\t\t\tand\n\t\t<</if>>\n\t\t$worn.under_lower.cn_name_cap',
     '<<if $worn.over_lower.name isnot "naked">>\n\t\t\t、\n\t\t<</if>>\n\t\t$worn.under_lower.cn_name_cap'),
    ('<<if $_part is "thighs" or $_part is "feet">>\n\t\t\tare\n',
     '<<if $_part is "thighs" or $_part is "feet">>\n\t\t\t' + Z + '\n'),
    ('<<else>>\n\t\t\tis\n\t\t<</if>>\n\t\t<<if $_semen gt 0>>',
     '<<else>>\n\t\t\t' + Z + '\n\t\t<</if>>\n\t\t<<if $_semen gt 0>>'),
    # ===== 礼仪 =====
    ('<<if $player.gender_appearance is "m">>\n\t\t\t\t\t\t\tBow\n',
     '<<if $player.gender_appearance is "m">>\n\t\t\t\t\t\t\t鞠躬\n'),
    ('<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\tbow\n\t\t<</if>>\n\t\t。',
     '<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\t鞠躬\n\t\t<</if>>\n\t\t。'),
    ('<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\tbow\n\t\t<</if>>\n\t\t吗？这会让我有被尊重的感觉。',
     '<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\t鞠躬\n\t\t<</if>>\n\t\t吗？这会让我有被尊重的感觉。'),
    # ===== 身体/名词 =====
    ('<<if $_thisSpecies.name is "plant">>\n\t\t\t\t\t\tnectar\n',
     '<<if $_thisSpecies.name is "plant">>\n\t\t\t\t\t\t花蜜\n'),
    ('<<if $_thisItem.name is "plant">>\n\t\t\t\t\t\tnectar\n',
     '<<if $_thisItem.name is "plant">>\n\t\t\t\t\t\t花蜜\n'),
    ('<<if maleChance() >= 100>>\n\t\t\t\t\t\t\tsemen\n',
     '<<if maleChance() >= 100>>\n\t\t\t\t\t\t\t精液\n'),
    ('<<elseif maleChance() gte 100>>\n\t\t\t\t\t\tsemen\n',
     '<<elseif maleChance() gte 100>>\n\t\t\t\t\t\t精液\n'),
    ('<<if $NPCList[0].breastsize is 0>>\n\t\t\t\t\t\tchest\n',
     '<<if $NPCList[0].breastsize is 0>>\n\t\t\t\t\t\t胸部\n'),
    ('<<else>>\n\tpussy\n<</if>>\n。\n<br><br>\n\n“我不会再对你手软了，”',
     '<<else>>\n\t小穴\n<</if>>\n。\n<br><br>\n\n“我不会再对你手软了，”'),
    ('<<else>>\n\t\tpussy\n\t<</if>>\n\t消失了。',
     '<<else>>\n\t\t小穴\n\t<</if>>\n\t消失了。'),
    ('<<if $player.penisExist>>\n\t\t<<penis>>\n\t<<else>>\n\t\tpussy\n\t<</if>>\n\t片刻，然后',
     '<<if $player.penisExist>>\n\t\t<<penis>>\n\t<<else>>\n\t\t小穴\n\t<</if>>\n\t片刻，然后'),
    ('<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\tpussy\n\t\t\t<</if>>\n\t\t\t<<set $pillory.tenant.lowerexposed to 2>>',
     '<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\t小穴\n\t\t\t<</if>>\n\t\t\t<<set $pillory.tenant.lowerexposed to 2>>'),
    ('<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\tpussy\n\t\t\t<</if>>\n\t\t\t和屁股',
     '<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\t小穴\n\t\t\t<</if>>\n\t\t\t和屁股'),
    ('<<if $NPCList[0].penis isnot "none">>\n\t<<print $NPCList[0].penisdesc>>\n<<else>>\n\tpussy\n<</if>>\n，<<he>>继续洗着碗。',
     '<<if $NPCList[0].penis isnot "none">>\n\t<<print $NPCList[0].penisdesc>>\n<<else>>\n\t小穴\n<</if>>\n，<<he>>继续洗着碗。'),
    ('<<if $pronoun is "m">>\n\tundies\n<<else>>\n\tpanties\n<</if>>\n，没错！',
     '<<if $pronoun is "m">>\n\t内裤\n<<else>>\n\t女式内裤\n<</if>>\n，没错！'),
    ('<<if $NPCList[0].gender is "m">>\n\t\t\t\tman\n\t\t\t<<else>>\n\t\t\t\twoman\n',
     '<<if $NPCList[0].gender is "m">>\n\t\t\t\t男人\n\t\t\t<<else>>\n\t\t\t\t女人\n'),
    # ===== 形容词 =====
    ('<<elseif $trauma gte (($traumamax / 5) * 1)>>\n\t\t\tbrittle\n',
     '<<elseif $trauma gte (($traumamax / 5) * 1)>>\n\t\t\t脆弱的\n'),
    ('<<if C.npc.Robin.dom lte 40>>\n\t\tmeek\n',
     '<<if C.npc.Robin.dom lte 40>>\n\t\t怯懦的\n'),
    ('<<elseif $player.penisExist>>\n\t\tsilently\n',
     '<<elseif $player.penisExist>>\n\t\t无声地\n'),
    # ===== 其他 =====
    ('<<if C.npc.Alex.dom gte 20>>\n\t\tmy\n', '<<if C.npc.Alex.dom gte 20>>\n\t\t我的\n'),
    ('<<elseif $settings.maleVictimChance lte 0>>\n\twomen\n<<else>>\n\t男人和女人的\n<</if>>\n的照片贴满了',
     '<<elseif $settings.maleVictimChance lte 0>>\n\t女人们的\n<<else>>\n\t男人和女人的\n<</if>>\n的照片贴满了'),
    ('<<elseif $settings.maleVictimChance lte 0>>\n\t\twomen\n\t<<else>>\n\t\t男人和女人的\n\t<</if>>\n\t照片贴满了',
     '<<elseif $settings.maleVictimChance lte 0>>\n\t\t女人们的\n\t<<else>>\n\t\t男人和女人的\n\t<</if>>\n\t照片贴满了'),
    ('<<else>>\n\t\t\t\t\tYou\n\t\t\t\t<</if>>\n\t\t\t\t捕捉到了',
     '<<else>>\n\t\t\t\t\t' + Z + '\n\t\t\t\t<</if>>\n\t\t\t\t捕捉到了'),
    ('<<if setup.clothes[_random_slot][_random_index].word is "an">>\n\t\t\t\tan\n\t\t\t<<else>>\n\t\t\t\ta\n',
     '<<if setup.clothes[_random_slot][_random_index].word is "an">>\n\t\t\t\t' + Z + '\n\t\t\t<<else>>\n\t\t\t\t' + Z + '\n'),
    ('<<if setup.clothes[_random_slot][_random_index].plural isnot 1>>\n\t\t\tit\n',
     '<<if setup.clothes[_random_slot][_random_index].plural isnot 1>>\n\t\t\t它\n'),
    ('<<else>>\n\t\tfinger\n\t<</if>>\n\t你，直到你精疲力尽。',
     '<<else>>\n\t\t用手指玩弄\n\t<</if>>\n\t你，直到你精疲力尽。'),
    ('<<elseif $finish is 1>>\n\tThe\n\t<<if $phase2 is 1>>',
     '<<elseif $finish is 1>>\n\t' + Z + '\n\t<<if $phase2 is 1>>'),
    ('<<if _pass gt 0>>\n\t\t\t终于，\n\t\t<<else>>\n\t\t\tThe\n\t\t<</if>>\n\t\t理发师',
     '<<if _pass gt 0>>\n\t\t\t终于，\n\t\t<<else>>\n\t\t\t' + Z + '\n\t\t<</if>>\n\t\t理发师'),
    ('<<else>>\n\t\t\tFilters\n\t\t<</if>>\n\t\t<<link "">>\n\t\t\t<<replace \'#filters\'>',
     '<<else>>\n\t\t\t筛选器\n\t\t<</if>>\n\t\t<<link "">>\n\t\t\t<<replace \'#filters\'>'),
    ('<<else>>\n\t\t\t\tHelp\n\t\t\t<</if>>\n\t\t\t<<link "">>\n\t\t\t\t<<toggleclass \'#shop-legend\'',
     '<<else>>\n\t\t\t\t帮助\n\t\t\t<</if>>\n\t\t\t<<link "">>\n\t\t\t\t<<toggleclass \'#shop-legend\''),
    ('<<if $player.penisExist and $player.vaginaExist>>\n\t\t被\n\t<<else>>\n\t\tis\n\t<</if>>\n\t再次脆弱地暴露在了空气中。',
     '<<if $player.penisExist and $player.vaginaExist>>\n\t\t被\n\t<<else>>\n\t\t' + Z + '\n\t<</if>>\n\t再次脆弱地暴露在了空气中。'),
    # ===== speechrammalentrance =====
    ("speechrammalentrance", "speechrammingentrance"),
]

total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            break

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [U12] 裸英文副词清理（72 处） -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# 复扫校验
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

ok = len(left) == 0
print("[U12] 修 %d 处  剩余裸英文=%d  passage=%d  %s" % (
    total, len(left),
    len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
if left:
    for x in left[:5]:
        print("   ", repr(x))
sys.exit(0 if ok else 1)
