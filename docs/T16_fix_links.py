"""T16：翻译 <<link>> 的英文按钮文本（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[T16] index 形态异常")
    sys.exit(1)

MARK = "[T16]"
g0 = H.unescape(data)
if MARK in g0:
    print("[T16] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
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
    ("Just clean <<him>>", "只是帮<<him>>清理"),
    ("Play with <<his>> nipples", "玩弄<<his>>的乳头"),
    ("DEBUG: Instagrow all plants here", "调试：让此处所有植物瞬间生长"),
]

total = 0
for en, cn in MAP:
    done = False
    # [[英文|  形态
    for a, b in ((H.escape("[[" + en + "|", quote=False), H.escape("[[" + cn + "|", quote=False)),
                 ("[[" + en + "|", "[[" + cn + "|")):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            done = True
            break
    if done:
        continue
    if "'" in en:
        e2 = en.replace("'", "\\'")
        for a, b in ((H.escape("[[" + e2 + "|", quote=False), H.escape("[[" + cn + "|", quote=False)),
                     ("[[" + e2 + "|", "[[" + cn + "|")):
            if a in data:
                c = data.count(a)
                data = data.replace(a, b)
                total += c
                done = True
                break
    if done:
        continue
    # <<link "英文"  形态
    for a, b in ((H.escape('<<link "' + en + '"', quote=False), H.escape('<<link "' + cn + '"', quote=False)),
                 ('<<link "' + en + '"', '<<link "' + cn + '"')):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            total += c
            break

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [T16] link 文本翻译 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))


def is_text(s):
    s = s.strip()
    if not s or re.search(r"[\u4e00-\u9fff]", s):
        return False
    if re.search(r"[`(){}\[\]]|=>|::|\.\w+\.|setup\.|\bvar\b|\bfunction\b|\breturn\b", s):
        return False
    if s.startswith("<<") or s.startswith("<"):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 3:
        return False
    return True


left = [m.group(1) for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]{3,200}?)\s*\|', g) if is_text(m.group(1))]
ok = len(left) == 0
print("[T16] 修 %d 处  剩余英文 link=%d  passage=%d  %s" % (
    total, len(left), len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
if left:
    for x in left[:5]:
        print("   ", repr(x))
sys.exit(0 if ok else 1)
