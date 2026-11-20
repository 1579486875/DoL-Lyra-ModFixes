"""T14：翻译 <<link>> / <<link "...">> 里的英文按钮文本（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[T14] index 形态异常")
    sys.exit(1)

MARK = "[T14]"
g0 = H.unescape(data)
if MARK in g0:
    print("[T14] 已存在，跳过")
    sys.exit(0)

# (英文, 中文) —— 都是 link 文本，独特，全局替换安全
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
    ("Confess that you\\'re naked", "承认你全身赤裸"),
    ("Confess that you\\'re exposed", "承认你暴露在外"),
    ("Confess that you\\'re covered in lewd fluids", "承认你满身淫液"),
    ("Just take the stones", "直接拿走石头"),
    ("Take the stones", "拿走石头"),
    ("Leave the fake stones on the plinth", "把假石头留在基座上"),
    ("Take the fake stones", "拿走假石头"),
    ("DEBUG: Instagrow all plants here", "调试：让此处所有植物瞬间生长"),
]

total = 0
print("=" * 90)
print("翻译 link 文本")
print("=" * 90)
for en, cn in MAP:
    hit = 0
    # 三种形态：单引号包裹、双引号包裹、含转义
    variants = [
        ("'" + en + "'", "'" + cn + "'"),
        ('"' + en + '"', '"' + cn + '"'),
        ("'" + en.replace("\\'", "'") + "'", "'" + cn + "'"),
        ('"' + en.replace("\\'", "'") + '"', '"' + cn + '"'),
    ]
    for a, b in variants:
        for aa, bb in ((H.escape(a, quote=False), H.escape(b, quote=False)), (a, b)):
            if aa in data:
                c = data.count(aa)
                data = data.replace(aa, bb)
                hit += c
                break
        if hit:
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {en[:55]!r}")

# 打标记
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [T14] link 文本翻译 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验（剩余英文 link 文本）")
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
for m in re.finditer(r'<<link\s+"([^"]{3,200})"', g):
    s = m.group(1)
    if is_text(s) and "fa-icon" not in s and "iconUi" not in s and "recipe_name" not in s and "@@" not in s:
        left.append(s)

print(f"  剩余 {len(left)} 条:")
for x in left:
    print(f"    {x!r}")

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if len(left) == 0 else 1)
