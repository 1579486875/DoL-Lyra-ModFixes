"""R15：查 forestShop-main 的完整实现。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. forestShop-main 完整定义")
print("=" * 95)
m = re.search(r'<<widget "forestShop-main">>(.*?)<</widget>>', g, re.S)
if m:
    wb = m.group(1)
    print(f"长度 {len(wb)}")
    print(wb[:3000])
else:
    print("❌ 不存在")
    for mm in list(re.finditer(r"forestShop", g))[:10]:
        print(f"  @{mm.start()}: {g[max(0,mm.start()-150):mm.start()+250]!r}")

print("\n" + "=" * 95)
print("2. 所有 forestShop* widget")
print("=" * 95)
for mm in re.finditer(r'<<widget "(forestShop[^"]*)"', g):
    print(f"  {mm.group(1)}")
