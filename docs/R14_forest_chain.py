"""R14：查 Forest Shop passage 的真实调用链 + _items 来源。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("=" * 95)
print("1. Forest Shop passage 全文")
print("=" * 95)
print(PASSAGES.get("Forest Shop", "❌ 不存在"))

print("\n" + "=" * 95)
print("2. generateshoppage 里 _items 的来源（完整开头 1200 字）")
print("=" * 95)
m = re.search(r'<<widget "generateshoppage">>(.*?)<</widget>>', g, re.S)
print(m.group(1)[:1200] if m else "❌")

print("\n" + "=" * 95)
print("3. 谁给 _items 赋值（含 updateShop / viewshop）")
print("=" * 95)
for mm in re.finditer(r"_items\s+to\s+setup", g):
    print(f"  @{mm.start()}: {g[max(0,mm.start()-300):mm.start()+400]!r}\n")

print("\n" + "=" * 95)
print("4. R10 注入是否在 index 里")
print("=" * 95)
print(f"  含 [R10]: {'[R10]' in g}")
for mm in list(re.finditer(r"\[R10\]", g))[:3]:
    print(f"  @{mm.start()}: {g[max(0,mm.start()-200):mm.start()+500]!r}")
