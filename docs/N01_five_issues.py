"""N01：查 5 个新问题。
1. `你告诉broad男人` —— broad 英文残留
2. `The 纤瘦的男人 masturbates` + `and` —— 英文残留
3. `<<social>>: <<if>>: Unexpected token '<<'` —— if 里有 <<
4. Corrupted variables
5. 确认 applyClothingShopFilter 是否已修（判断用户装的是哪个包）
"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("=" * 95)
print("5. 确认 applyClothingShopFilter（判断用户装的是哪个包）")
print("=" * 95)
print(f"  applyClothingShopFilters（带 s）: {g.count('applyClothingShopFilters')}")
print(f"  applyClothingShopFilter(_items): {g.count('applyClothingShopFilter(_items)')}")
print(f"  applyClothingShopFilter（不带 s 的总数）: {len(re.findall(r'applyClothingShopFilter(?![sA-Za-z])', g))}")

print("\n" + "=" * 95)
print("1. `broad` 英文残留")
print("=" * 95)
n = 0
for m in re.finditer(r"broad", g):
    ctx = g[max(0, m.start() - 120):m.start() + 120]
    if re.search(r"[\u4e00-\u9fff]", ctx):
        n += 1
        if n <= 6:
            print(f"  @{m.start()}: {ctx!r}")
print(f"  共 {n} 处（在中文上下文里的 broad）")

print("\n" + "=" * 95)
print("2a. `The <中文>` 形式")
print("=" * 95)
n2 = 0
for m in re.finditer(r"\bThe\s+[\u4e00-\u9fff]", g):
    n2 += 1
    if n2 <= 8:
        print(f"  @{m.start()}: {g[max(0,m.start()-100):m.start()+150]!r}")
print(f"  共 {n2} 处")

print("\n" + "=" * 95)
print("2b. `masturbates` 英文残留")
print("=" * 95)
n2b = 0
for m in re.finditer(r"masturbates", g):
    ctx = g[max(0, m.start() - 150):m.start() + 150]
    if re.search(r"[\u4e00-\u9fff]", ctx):
        n2b += 1
        if n2b <= 5:
            print(f"  @{m.start()}: {ctx!r}")
print(f"  共 {n2b} 处")

print("\n" + "=" * 95)
print("2c. `中文 and 中文` 形式")
print("=" * 95)
n2c = 0
for m in re.finditer(r"[\u4e00-\u9fff]\s+and\s+[\u4e00-\u9fff]", g):
    n2c += 1
    if n2c <= 8:
        print(f"  @{m.start()}: {g[max(0,m.start()-80):m.start()+100]!r}")
print(f"  共 {n2c} 处")

print("\n" + "=" * 95)
print("3. <<if>> 里出现 << 的（Unexpected token '<<'）")
print("=" * 95)
n3 = 0
for m in re.finditer(r"<<if\b([^<>]{0,600}?)>>", g):
    body = m.group(1)
    # 挖掉字符串
    s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
    s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
    if "<<" in s or "<" in s:
        n3 += 1
        if n3 <= 10:
            print(f"  @{m.start()}: {m.group(0)[:250]!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("4. relation-box widget 的 <<if>>")
print("=" * 95)
for pname, body in PASSAGES.items():
    mm = re.search(r'<<widget "relation-box">>(.*?)<</widget>>', body, re.S)
    if not mm:
        continue
    wb = mm.group(1)
    print(f"  在 [{pname}]，长度 {len(wb)}")
    for m in re.finditer(r"<<if\b([^<>]{0,400}?)>>", wb):
        b = m.group(1)
        s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), b)
        s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
        if "<" in s:
            print(f"    ❌ {m.group(0)[:250]!r}")
    break
