"""K01：查 TweeReplacer 报错的 4 个锚点在不在。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)
print(f"passage {len(PASSAGES)}\n")

TARGETS = [
    # (模组, 类型, 要找的字符串, 所在 passage)
    ("DoLSims", "findRegex", r'<<widget "fallentransform">>\s*<<if $angel gte 6>>', "Transformation Widgets"),
    ("DomRobin", "findString", "<<if $robinpaid isnot 1 and $robindebtknown is 1>>", "Bailey's Office"),
    ("DomRobin", "findString", "<<if $robinpaid isnot 1>>", "Widgets Robin"),
    ("DomRobin", "findRegex", "canAfford(300", "Ocean Breeze"),
]

print("=" * 95)
print("1. 逐个检查锚点")
print("=" * 95)
for mod, kind, needle, pname in TARGETS:
    print(f"\n[{mod}] {kind}")
    print(f"  找: {needle!r}")
    print(f"  在: {pname!r}")
    body = PASSAGES.get(pname)
    if body is None:
        print(f"  ❌ passage 不存在！")
        continue
    # 精确找
    if kind == "findString":
        found = needle in body
        print(f"  {'✅ 找到' if found else '❌ 没找到'}")
        if not found:
            # 找相似
            key = re.sub(r"[^\w]", "", needle)[:30]
            print(f"  相似内容:")
            for mm in re.finditer(r"<<if [^>]{0,200}>>", body):
                if "robinpaid" in mm.group(0) or "robindebt" in mm.group(0):
                    print(f"    {mm.group(0)!r}")
    else:
        found = re.search(needle, body)
        print(f"  {'✅ 找到' if found else '❌ 没找到'}")
        if not found:
            # 找 widget 定义
            mm = re.search(r'<<widget "fallentransform">>[^<]{0,200}', body)
            if mm:
                print(f"  实际: {mm.group(0)[:250]!r}")
            mm2 = re.search(r"<<if \$angel[^>]{0,80}>>", body)
            if mm2:
                print(f"  实际 angel 条件: {mm2.group(0)!r}")
            # canAfford
            for mm3 in list(re.finditer(r"[^;]{0,80}canAfford[^;]{0,120}", body))[:3]:
                print(f"  实际 canAfford: {mm3.group(0)!r}")

print("\n" + "=" * 95)
print("2. 相关 passage 是否存在")
print("=" * 95)
for p in ("Transformation Widgets", "Bailey's Office", "Widgets Robin", "Ocean Breeze"):
    print(f"  {'OK ' if p in PASSAGES else 'MISS'} {p!r}")
