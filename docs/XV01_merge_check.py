"""把最后一批 displayName 并入 XK01_more_dn.py，并抽查 either 的 110 处。"""
import html
import os
import re
import sys

XK = r"E:\TAML\_dol\work\XK01_more_dn.py"
APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"

EXTRA = '''    "Starting season:": "起始季节：",
    "Game difficulty:": "游戏难度：",
    "Ironman mode:": "铁人模式：",
    "Natural Skintone:": "自然肤色：",
    "Freckles:": "雀斑：",
    "Cost of lewd clothes:": "淫秽衣物价格：",
    "Cost of school clothes:": "校服价格：",
    "Cost of underwear:": "内衣价格：",
    "Mouth:": "口腔：",
    "Hands:": "手部：",
    "Nipples:": "乳头：",
    "Penis:": "阴茎：",
    "Vagina:": "阴道：",
    "Anus:": "肛门：",
    "Thighs:": "大腿：",
'''

# 1) 并入 XK01
s = open(XK, encoding="utf-8").read()
if "Starting season:" not in s:
    anchor = '    "Combat:": "战斗：",\n}'
    if anchor in s:
        s = s.replace(anchor, '    "Combat:": "战斗：",\n' + EXTRA + '}', 1)
        open(XK, "w", encoding="utf-8").write(s)
        print("✅ 已并入 XK01_more_dn.py")
    else:
        print("⚠️ 未找到锚点")
else:
    print("（已存在）")

# 2) 抽查 either 的 110 处
print("\n" + "=" * 88)
print("抽查 either() 全角逗号")
print("=" * 88)
z = zipfile = None
import zipfile as _z
zz = _z.ZipFile(APK)
g = html.unescape(zz.read("assets/www/index.html").decode("utf-8", "replace"))

samples = []
for mm in re.finditer(r"<<[^>]{0,600}?>>", g):
    macro = mm.group(0)
    if "either(" not in macro:
        continue
    k = macro.find("either(")
    i2 = k + len("either(")
    d2 = 1
    while i2 < len(macro) and d2 > 0:
        if macro[i2] == "(":
            d2 += 1
        elif macro[i2] == ")":
            d2 -= 1
        i2 += 1
    inner = macro[k + len("either("):i2 - 1]
    base = re.sub(r'"(?:[^"\\]|\\.)*"', '""', inner)
    base = re.sub(r"'(?:[^'\\]|\\.)*'", "''", base)
    if "，" in base:
        samples.append(macro)

print(f"共 {len(samples)} 处，抽前 6 个：")
for x in samples[:6]:
    print(f"\n  {x[:250]!r}")
