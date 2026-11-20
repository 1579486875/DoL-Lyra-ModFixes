"""T15：修正 T14 的替换形态 —— link 文本是 [[文本|目标]]，无引号。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[T15] index 形态异常")
    sys.exit(1)

MARK = "[T15]"
g0 = H.unescape(data)
if MARK in g0:
    print("[T15] 已存在，跳过")
    sys.exit(0)

MAP = [
    ("Investigate the staircase", "查看楼梯"),
    ("Shout for Eden", "呼喊伊甸"),
    ("Insist on the Remy Estate", "坚持要去雷米庄园"),
    ("Try the door", "试着推门"),
    ("Change displayed produce", "更换展示的农产品"),
    ("Strip and get in bed", "脱光衣服上床"),
    ("Porn-decorated cell", "淫秽装饰的牢房"),
    ("Ask about replacement wishing stones", "询问替换用的许愿石"),
    ("Enter the pool room", "进入泳池房间"),
    ("Hang up coat", "挂起外套"),
    ("Ask how much they offer for old clothes", "问旧衣服能换多少"),
    ("Confess your crimes", "坦白你的罪行"),
    ("Confess to spying on Jordan", "承认你在监视约旦"),
    ("Confess that you're naked", "承认你全身赤裸"),
    ("Confess that you're exposed", "承认你暴露在外"),
    ("Confess that you're covered in lewd fluids", "承认你满身淫液"),
    ("Just take the stones", "直接拿走石头"),
    ("Take the stones", "拿走石头"),
    ("Leave the fake stones on the plinth", "把假石头留在基座上"),
    ("Take the fake stones", "拿走假石头"),
    ("Push Avery into the pool", "把艾弗里推进泳池"),
    ("Call out Remy instead", "改喊雷米"),
    # 含宏的：保留宏，只翻外围
    ("Just clean <<him>>", "只是帮<<him>>清理"),
    ("Play with <<his>> nipples", "玩弄<<his>>的乳头"),
]

total = 0
print("=" * 90)
print("按 [[文本| 形态替换")
print("=" * 90)
for en, cn in MAP:
    hit = 0
    # 主形态：[[英文|
    for a, b in ((H.escape("[[" + en + "|", quote=False), H.escape("[[" + cn + "|", quote=False)),
                 ("[[" + en + "|", "[[" + cn + "|")):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    # 兼容转义单引号
    if not hit and "'" in en:
        e2 = en.replace("'", "\\'")
        for a, b in ((H.escape("[[" + e2 + "|", quote=False), H.escape("[[" + cn + "|", quote=False)),
                     ("[[" + e2 + "|", "[[" + cn + "|")):
            if a in data:
                c = data.count(a)
                data = data.replace(a, b)
                hit += c
                break
    if hit:
        total += hit
        print(f"  OK {hit}x  {en[:55]!r}")
    else:
        print(f"  MISS     {en[:55]!r}")

# 也处理 <<link "文本">> 形态
print("\n" + "=" * 90)
print("按 <<link \"文本\">> 形态再试一遍")
print("=" * 90)
for en, cn in MAP:
    for a, b in ((H.escape('<<link "' + en + '"', quote=False), H.escape('<<link "' + cn + '"', quote=False)),
                 ('<<link "' + en + '"', '<<link "' + cn + '"')):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            print(f"  OK {c}x  <<link {en[:45]!r}")
            break

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [T15] link 文本翻译 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)


def is_text(s):
    s = s.strip()
    if not s or re.search(r"[\u4e00-\u9fff]", s):
        return False
    if re.search(r"[$`(){}\[\]]|=>|::|\.\w+\.|setup\.|\bvar\b|\bfunction\b|\breturn\b|\bnull\b|\bundefined\b", s):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 3:
        return False
    if re.fullmatch(r"[A-Za-z0-9_.\-\s]+", s) and " " not in s:
        return False
    return True


left = []
for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]{3,200}?)\s*\|', g):
    if is_text(m.group(1)):
        left.append(m.group(1))

print(f"  剩余 {len(left)} 条:")
for x in left:
    print(f"    {x!r}")
print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if len(left) == 0 else 1)
