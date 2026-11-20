"""W05：修 3 处 tooltip/正文英文（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[W05] index 形态异常")
    sys.exit(1)

MARK = "[W05]"
g0 = H.unescape(data)
if MARK in g0:
    print("[W05] 已存在，跳过")
    sys.exit(0)

# ---- 1. setup.colourName(.colour) 代码泄漏 ----
FIX1 = [
    ("世界变得阴暗，失去了setup.colourName(.colour)。",
     "世界变得阴暗，失去了色彩。"),
]

# ---- 2. 随机化 tooltip 全翻 ----
FIX2 = [
    ("Randomises the player character's appearance, including hair, eyes, skin colour, gender, and body part sizes. 身体 size, gender appearance, genitalia, and base skin colour cannot be changed after starting the game.",
     "随机化玩家的外貌，包括头发、眼睛、肤色、性别以及身体部位尺寸。"
     "身体的尺寸、性别外观、生殖器以及基础肤色在开始游戏后无法更改。"),
]

# ---- 3. Increasing / Decreasing tooltip ----
FIX3 = [
    ("Increasing your $_stat:", "提升你的$_stat："),
    ("Decreasing your $_stat:", "降低你的$_stat："),
]

total = 0
print("=" * 90)
print("修复")
print("=" * 90)

for group, name in ((FIX1, "1. colourName 泄漏"),
                    (FIX2, "2. 随机化 tooltip"),
                    (FIX3, "3. Increasing/Decreasing")):
    print(f"\n[{name}]")
    for old, new in group:
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

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [W05] tooltip 英文清理 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
checks = {
    "setup.colourName(.colour)": "setup.colourName(.colour)",
    "Randomises the player": "Randomises the player",
    "Increasing your $_stat": "Increasing your $_stat",
    "Decreasing your $_stat": "Decreasing your $_stat",
}
for label, pat in checks.items():
    n = g.count(pat)
    print(f"  {'OK ' if n == 0 else 'FAIL'} {label}: {n}")

# 复扫 tooltip
n_mouse = 0
for m in re.finditer(r'<mouse[^>]*>(.*?)</mouse>', g, re.S):
    body = re.sub(r"<[^>]+>", " ", m.group(1))
    body = re.sub(r"<<[^>]*>>", " ", body)
    if len(re.findall(r"[A-Za-z]{3,}", body)) >= 3 and not re.search(r"[\u4e00-\u9fff]", body):
        n_mouse += 1

print(f"\n  剩余纯英文 <mouse>: {n_mouse}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if all(g.count(p) == 0 for p in checks.values()) else 1)
