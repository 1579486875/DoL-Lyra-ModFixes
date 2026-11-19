"""第 40 轮：验证 5 个可疑判断的数据来源。

可疑点：
  1. $temple_wall_victim is "男孩"
  2. $worn.genitals.name is "贞操锁寄生虫"
  3. <<case "巨鹰">> / <<case "黑狼">>  (NPCName[].name)
  4. $earSlime.event is "用精子灌入..."
  5. _fatherName === "你自己"
"""
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

CASES = [
    ("$temple_wall_victim",
     r"\$temple_wall_victim"),
    ("$worn.genitals.name",
     r"\$worn\.genitals\.name"),
    ("$NPCName[].name (巨鹰/黑狼)",
     r'"(?:巨鹰|黑狼)"'),
    ("$earSlime.event",
     r"\$earSlime\.event"),
    ("_fatherName",
     r"_fatherName"),
]

for label, pat in CASES:
    print("=" * 90)
    print(f"{label}")
    print("=" * 90)
    print("\n[modded 赋值处]")
    # 找赋值
    n = 0
    for m in re.finditer(r"<<set\s+" + pat + r"\s+to\s+([^>]{0,150})>>", mg):
        n += 1
        if n <= 5:
            print(f"  {m.group(0)[:180]!r}")
    if not n:
        # 找 JS 赋值
        for m in re.finditer(pat + r"\s*=\s*([^;\n]{0,120})", mg):
            n += 1
            if n <= 5:
                print(f"  {m.group(0)[:180]!r}")
    print(f"  共 {n} 处赋值")

    print("\n[vanilla 赋值处]")
    n2 = 0
    for m in re.finditer(r"<<set\s+" + pat + r"\s+to\s+([^>]{0,150})>>", vg):
        n2 += 1
        if n2 <= 3:
            print(f"  {m.group(0)[:180]!r}")
    if not n2:
        for m in re.finditer(pat + r"\s*=\s*([^;\n]{0,120})", vg):
            n2 += 1
            if n2 <= 3:
                print(f"  {m.group(0)[:180]!r}")
    print(f"  共 {n2} 处赋值")
    print()

# 专门查 genitals 的 name 属性
print("=" * 90)
print("genitals 对象的定义（看 name 是否为英文）")
print("=" * 90)
for m in list(re.finditer(r'name:\s*"([^"]+)"[^}]{0,200}genitals', mg))[:3]:
    print(f"  {m.group(0)[:200]!r}")
for m in list(re.finditer(r'genitals:\s*\{[^}]{0,300}', mg))[:3]:
    print(f"  {m.group(0)[:300]!r}")

# 查 earSlime.event 的候选值
print("\n" + "=" * 90)
print("earSlime event 候选值")
print("=" * 90)
cands = set(re.findall(r'_earSlimeEvents?\s*=\s*\[([^\]]{0,500})\]', mg))
for c in list(cands)[:2]:
    print(f"  {c[:400]!r}")

# 查 temple_wall_victim 的候选
print("\n" + "=" * 90)
print("temple_wall_victim 赋值上下文")
print("=" * 90)
for m in list(re.finditer(r"temple_wall_victim", mg))[:6]:
    print(f"  {mg[max(0,m.start()-150):m.start()+150]!r}")
