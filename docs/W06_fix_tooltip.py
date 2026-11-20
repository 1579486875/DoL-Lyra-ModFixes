"""W06：修 tooltip 英文 + 正文代码泄漏（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[W06] index 形态异常")
    sys.exit(1)

MARK = "[W06]"
g0 = H.unescape(data)
if MARK in g0:
    print("[W06] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

FIXES = [
    # 1. 正文里泄漏的代码
    ("世界变得阴暗，失去了setup.colourName(.colour)。",
     "世界变得阴暗，失去了色彩。"),
    # 2. 随机化设置的 tooltip（整段英文 + 中间插了「身体」）
    ("Randomises the player character's appearance, including hair, eyes, skin colour, gender, and body part sizes. 身体 size, gender appearance, genitalia, and base skin colour cannot be changed after starting the game.",
     "随机化玩家的外貌，包括头发、眼睛、肤色、性别以及身体部位尺寸。"
     "身体的尺寸、性别外观、生殖器以及基础肤色在开始游戏后无法更改。"),
    # 3. 属性变化 tooltip 的英文前缀
    ("Increasing your $_stat:", "提升你的$_stat："),
    ("Decreasing your $_stat:", "降低你的$_stat："),
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
    H.escape('<!-- [W06] tooltip 英文 + 正文代码泄漏 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))

g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
BAD = {
    "colourName泄漏": g.count("setup.colourName(.colour)"),
    "Randomises": g.count("Randomises the player"),
    "Increasing": g.count("Increasing your $_stat"),
    "Decreasing": g.count("Decreasing your $_stat"),
}
ok = all(v == 0 for v in BAD.values())
print("[W06] 修 %d 处  passage=%d  %s  %s" % (
    total, len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "  ".join("%s=%d" % (k, v) for k, v in BAD.items()),
    "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
