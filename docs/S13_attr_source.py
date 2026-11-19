"""轮13：查 tentacles.desc / wardrobes.name 等属性表的数据语言。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

CASES = [
    ("tentacle desc", r"desc:\s*\"([^\"]{0,40})\"[^}]{0,200}tentacle"),
    ("tentacle 表", r"tentacleDesc\w*\s*=\s*[\[\{](.{0,600})"),
    ("wardrobe name", r"wardrobes\s*=\s*\{(.{0,800})"),
    ("tentacle fullDesc", r"fullDesc:\s*\"([^\"]{0,60})\""),
]

for label, pat in CASES:
    print("=" * 90)
    print(label)
    print("=" * 90)
    for tag, g in (("modded", mg), ("vanilla", vg)):
        hits = re.findall(pat, g, re.S)
        cn = sum(1 for h in hits if CJK.search(h))
        en = sum(1 for h in hits if re.search(r"[A-Za-z]", h))
        print(f"  {tag}: {len(hits)} 处  含中文 {cn}  含英文 {en}")
        for h in hits[:2]:
            print(f"    {h[:200]!r}")
    print()

# 直接找 $tentacles 的初始化
print("=" * 90)
print("$tentacles 初始化")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for m in list(re.finditer(r"tentacles\s*[:=]", g))[:3]:
        print(f"  {g[max(0,m.start()-100):m.start()+400]!r}")

# 找 wards 的 name 定义
print("\n" + "=" * 90)
print("wardrobes 的 name 字段")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for m in list(re.finditer(r"wardrobes?\s*=\s*\{", g))[:2]:
        seg = g[m.start():m.start() + 900]
        print(f"  {seg[:700]!r}")

# 触手描述表
print("\n" + "=" * 90)
print("触手描述候选值（苍白色 / 金属色）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for kw in ["苍白色", "金属色", "pale", "metallic"]:
        n = g.count(kw)
        if n:
            print(f"  {kw!r}: {n} 次")
            m = re.search(re.escape(kw), g)
            if m:
                print(f"    {g[max(0,m.start()-150):m.start()+150]!r}")
