"""第 47 轮：查 penisdesc 的完整候选值，确认 includes("穿戴式") 是否正确。"""
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
print("1) penisdesc 的所有可能值")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    # setup.penisDescList 或类似
    for pat in [r"(?:setup\.)?penisDesc\w*\s*=\s*\[([^\]]{0,800})\]",
                r"(?:setup\.)?penisdesc\w*\s*=\s*\[([^\]]{0,800})\]"]:
        for m in re.finditer(pat, g, re.I):
            print(f"  表: {m.group(1)[:600]!r}")
    # 找 'strapon' 的定义
    for m in list(re.finditer(r'strapon', g))[:10]:
        ctx = g[max(0, m.start() - 120):m.start() + 120]
        if ":" in ctx and ('"' in ctx):
            print(f"  strapon 上下文: {ctx!r}")
            break

print("\n" + "=" * 90)
print("2) '穿戴式' 出现的上下文（前 5 处）")
print("=" * 90)
for m in list(re.finditer(r"穿戴式", mg))[:5]:
    print(f"  @{m.start()}: {mg[max(0,m.start()-150):m.start()+150]!r}")

print("\n" + "=" * 90)
print("3) 关键判断：.includes(\"穿戴式\") vs .includes(\"strapon\")")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    a = len(re.findall(r'\.includes\(\s*"穿戴式"\s*\)', g))
    b = len(re.findall(r'\.includes\(\s*"strapon"\s*\)', g))
    c = len(re.findall(r'\.includes\(\s*"假阳具"\s*\)', g))
    print(f"  {label}: includes('穿戴式') {a} / includes('strapon') {b} / includes('假阳具') {c}")

print("\n" + "=" * 90)
print("4) penisdesc 被赋值成什么（生成逻辑）")
print("=" * 90)
for m in list(re.finditer(r"penisdesc\s*[:=]", mg))[:8]:
    print(f"  {mg[max(0,m.start()-200):m.start()+250]!r}")
    print()

print("\n" + "=" * 90)
print("5) 装备类物品的 name 与 penisdesc 的对照")
print("=" * 90)
# 找 strapon 物品定义
for m in list(re.finditer(r'name:\s*"([^"]*[Ss]trapon[^"]*)"', mg))[:5]:
    print(f"  {m.group(1)!r}")
for m in list(re.finditer(r'variable:\s*"([^"]*strapon[^"]*)"', mg))[:5]:
    print(f"  variable {m.group(1)!r}")
