"""E02：修 18 处「英文标识符被翻译成中文」的致命语法错误。"""
import html as H
import json
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r"<tw-passagedata", data)) < 10000:
    print("❌ index 不是明文 passage 形态")
    sys.exit(1)

g = H.unescape(data)

# 精确修复表（原文 -> 正确代码）
FIXES = [
    # 1. _lower. 被翻成 _下体。（全角句号！）
    ("<<set _下体。integrity -= 10>>", "<<set _lower.integrity -= 10>>"),
    ("<<if _下体。integrity lte 0>>", "<<if _lower.integrity lte 0>>"),
    ("<<if _下体。plural isnot 1>>", "<<if _lower.plural isnot 1>>"),

    # 2. $speechrammal 被拆
    ("<<set $speech冲撞着entrance to 1>>", "<<set $speechrammalentrance to 1>>"),

    # 3. 全角逗号
    ("<<switch Math.clamp($_精液， 1, 5)>>", "<<switch Math.clamp($_semen, 1, 5)>>"),

    # 4. C.npc.Robin / Avery 被翻
    ("<<if C.npc.罗宾。trauma gte 50>>", "<<if C.npc.Robin.trauma gte 50>>"),
    ("<<elseif C.npc.罗宾。dom gte 50>>", "<<elseif C.npc.Robin.dom gte 50>>"),
    ("<<elseif C.npc.艾弗里。rage gte 20 and $averyragerevealed is 1>>",
     "<<elseif C.npc.Avery.rage gte 20 and $averyragerevealed is 1>>"),
    ("<<if C.npc.罗宾借走了。trauma gte 20>>", "<<if C.npc.Robin.trauma gte 20>>"),
    ("<<if C.npc.罗宾借走了。trauma gte 60>>", "<<if C.npc.Robin.trauma gte 60>>"),

    # 5. $bird.firepit_front 被翻
    ("$bird.火坑前面。items.length gte 1", "$bird.firepit_front.items.length gte 1"),

    # 6. $enemyarousal 被拆
    ("<<if $ene我的arousal gte $enemyarousalmax>>",
     "<<if $enemyarousal gte $enemyarousalmax>>"),

    # 7. $skin.forehead 被翻
    ('$skin.额头上。special isnot "island" and $skin.额头上。pen isnot "brand" and $skin.额头上。pen isnot "tattoo" and $skin.额头上。pen isnot "magic"',
     '$skin.forehead.special isnot "island" and $skin.forehead.pen isnot "brand" and $skin.forehead.pen isnot "tattoo" and $skin.forehead.pen isnot "magic"'),

    # 8. applyClothingShopFilter 被翻
    ("<<set _items = applyClothingShop过滤(_items)>>",
     "<<set _items = applyClothingShopFilter(_items)>>"),

    # 9. tanningEnabled 被翻
    ("<<set _modeloptions.tanning启用d to false>>",
     "<<set _modeloptions.tanningEnabled to false>>"),

    # 10. order: 被翻成 次序:
    ('{ prop: "price", 次序: \'asc\', enabled: false }',
     '{ prop: "price", order: \'asc\', enabled: false }'),
]

print("=" * 90)
print("修复 18 处")
print("=" * 90)
total = 0
miss = []
for old, new in FIXES:
    found = False
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            found = True
            print(f"  ✅ {c}x {old[:70]!r}")
            break
    if not found:
        miss.append(old)
        print(f"  ⚠️ 未命中 {old[:70]!r}")

# 通用清理：全角标点在宏内
print("\n" + "=" * 90)
print("通用清理：宏内的全角标点")
print("=" * 90)
g2 = H.unescape(data)
n_gen = 0
# 全角逗号/句号/冒号/分号 在 <<...>> 里
for m in list(re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,600}?)>>", g2)):
    body = m.group(2)
    if not re.search(r"[，。：；！？]", body):
        continue
    # 只处理代码位置（挖掉字符串后仍有全角标点）
    stripped = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', '""', body)
    if not re.search(r"[，。：；！？]", stripped):
        continue
    print(f"  ⚠️ {m.group(0)[:160]!r}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n✅ 共修 {total} 处")

# 校验
gg = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
print(f"  passage: {len(re.findall(r'<tw-passagedata', open(HTML,'rb').read().decode('utf-8','replace')))}")
REMAIN = ["_下体。", "C.npc.罗宾。", "C.npc.艾弗里。", "$bird.火坑前面。",
          "$ene我的arousal", "$skin.额头上。", "applyClothingShop过滤",
          "tanning启用d", "次序:", "$speech冲撞着", "_精液，"]
for kw in REMAIN:
    c = gg.count(kw)
    print(f"  {'✅' if c == 0 else '❌'} {kw!r}: {c}")
