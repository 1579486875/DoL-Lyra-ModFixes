"""第 41 轮：查 $worn.genitals.name 和 $NPCName[].name 的数据源。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

print("=" * 90)
print("1) 贞操锁寄生虫 物品定义")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for m in list(re.finditer(r'"贞操锁寄生虫"', g))[:5]:
        print(f"  @{m.start()}: {g[max(0,m.start()-250):m.start()+150]!r}")
    # vanilla 里这个物品叫什么
    if label == "vanilla":
        for m in list(re.finditer(r'name:\s*"([^"]*[Pp]arasite[^"]*)"', g))[:5]:
            print(f"  英文名: {m.group(1)!r}")
            print(f"    {g[max(0,m.start()-200):m.start()+300]!r}")

print("\n" + "=" * 90)
print("2) vanilla 里对应的物品英文名")
print("=" * 90)
# vanilla 里 genitals 数组
for m in list(re.finditer(r"genitals:\s*\[([^\]]{0,3000})\]", vg))[:2]:
    print(f"  {m.group(1)[:800]!r}")

print("\n" + "=" * 90)
print("3) NPCName[].name 的来源")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    # NPCName 的 name 字段初始化
    for m in list(re.finditer(r"name:\s*\"(?:巨鹰|黑狼|Great Hawk|Black Wolf)\"", g))[:5]:
        print(f"  {m.group(0)!r}  @{m.start()}")
        print(f"    {g[max(0,m.start()-200):m.start()+250]!r}")
    # 找 npcName 表
    for m in list(re.finditer(r"(?:setup\.)?NPCName(?:List)?\s*=\s*\[", g))[:2]:
        print(f"  NPCName 表 @{m.start()}: {g[m.start():m.start()+300]!r}")

print("\n" + "=" * 90)
print("4) 'Ivory Wraith' 对照（这个两边都是英文）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    n_cn = len(re.findall(r'"象牙幽灵"', g))
    n_en = len(re.findall(r'"Ivory Wraith"', g))
    print(f"  {label}: 中文 '象牙幽灵' {n_cn} / 英文 'Ivory Wraith' {n_en}")

print("\n" + "=" * 90)
print("5) 'Night Monster' 对照")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    n_cn = len(re.findall(r'"夜魔"', g))
    n_en = len(re.findall(r'"Night Monster"', g))
    print(f"  {label}: 中文 '夜魔' {n_cn} / 英文 'Night Monster' {n_en}")
