"""U11：修最后 12 处裸英文。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[U11] index 形态异常")
    sys.exit(1)

MARK = "[U11]"
g0 = H.unescape(data)
if MARK in g0:
    print("[U11] 已存在，跳过")
    sys.exit(0)

FIXES = [
    # ---- finger：后面紧跟「你」，应为「用手指玩弄」----
    ('<<else>>\n\t\tfinger\n\t<</if>>\n\t你，直到你精疲力尽。',
     '<<else>>\n\t\t用手指玩弄\n\t<</if>>\n\t你，直到你精疲力尽。'),
    # ---- The ×2：中文不需要冠词，用零宽占位 ----
    ('<<elseif $finish is 1>>\n\tThe\n\t<<if $phase2 is 1>>',
     '<<elseif $finish is 1>>\n\t\u200b\n\t<<if $phase2 is 1>>'),
    ('<<if _pass gt 0>>\n\t\t\t终于，\n\t\t<<else>>\n\t\t\tThe\n\t\t<</if>>\n\t\t理发师',
     '<<if _pass gt 0>>\n\t\t\t终于，\n\t\t<<else>>\n\t\t\t\u200b\n\t\t<</if>>\n\t\t理发师'),
    # ---- Filters ----
    ('<<else>>\n\t\t\tFilters\n\t\t<</if>>\n\t\t<<link "">>\n\t\t\t<<replace \'#filters\'>',
     '<<else>>\n\t\t\t筛选器\n\t\t<</if>>\n\t\t<<link "">>\n\t\t\t<<replace \'#filters\'>'),
    # ---- Help ----
    ('<<else>>\n\t\t\t\tHelp\n\t\t\t<</if>>\n\t\t\t<<link "">>\n\t\t\t\t<<toggleclass \'#shop-legend\'',
     '<<else>>\n\t\t\t\t帮助\n\t\t\t<</if>>\n\t\t\t<<link "">>\n\t\t\t\t<<toggleclass \'#shop-legend\''),
    # ---- pussy ×3 ----
    ('<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\tpussy\n\t\t\t<</if>>\n\t\t\t<<set $pillory.tenant.lowerexposed to 2>>',
     '<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\t小穴\n\t\t\t<</if>>\n\t\t\t<<set $pillory.tenant.lowerexposed to 2>>'),
    ('<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\tpussy\n\t\t\t<</if>>\n\t\t\t和屁股',
     '<<if $pillory.tenant.person.gender is "m">>\n\t\t\t\t$pillory.tenant.person.penisdesc\n\t\t\t<<else>>\n\t\t\t\t小穴\n\t\t\t<</if>>\n\t\t\t和屁股'),
    ('<<if $NPCList[0].penis isnot "none">>\n\t<<print $NPCList[0].penisdesc>>\n<<else>>\n\tpussy\n<</if>>\n，<<he>>继续洗着碗。',
     '<<if $NPCList[0].penis isnot "none">>\n\t<<print $NPCList[0].penisdesc>>\n<<else>>\n\t小穴\n<</if>>\n，<<he>>继续洗着碗。'),
    # ---- bow ×2 ----
    ('<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\tbow\n\t\t<</if>>\n\t\t。',
     '<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\t鞠躬\n\t\t<</if>>\n\t\t。'),
    ('<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\tbow\n\t\t<</if>>\n\t\t吗？这会让我有被尊重的感觉。',
     '<<if $player.gender_appearance is "f">>\n\t\t\t屈膝礼\n\t\t<<else>>\n\t\t\t鞠躬\n\t\t<</if>>\n\t\t吗？这会让我有被尊重的感觉。'),
    # ---- undies / panties ----
    ('<<if $pronoun is "m">>\n\tundies\n<<else>>\n\tpanties\n<</if>>\n，没错！',
     '<<if $pronoun is "m">>\n\t内裤\n<<else>>\n\t女式内裤\n<</if>>\n，没错！'),
    # ---- is ----
    ('<<if $player.penisExist and $player.vaginaExist>>\n\t\t被\n\t<<else>>\n\t\tis\n\t<</if>>\n\t再次脆弱地暴露在了空气中。',
     '<<if $player.penisExist and $player.vaginaExist>>\n\t\t被\n\t<<else>>\n\t\t\u200b\n\t<</if>>\n\t再次脆弱地暴露在了空气中。'),
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
        print(f"  OK {hit}x  {old[:55]!r}")
    else:
        print(f"  MISS     {old[:55]!r}")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [U11] 裸英文清理第三批 -->' + '<<widget "generateshoppage">>', quote=False), 1)

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
for w, c in Counter(left).most_common(20):
    print(f"  {c:>3}  {w!r}")

# 安全阀
print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
