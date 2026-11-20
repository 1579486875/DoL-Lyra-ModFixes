"""N04：查 desc / descCN 的输出位置。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. descCN 的赋值位置")
print("=" * 95)
for m in re.finditer(r"descCN\s*(?:to|=)", g):
    print(f"  @{m.start()}: {g[max(0,m.start()-200):m.start()+200]!r}\n")

print("=" * 95)
print("2. <<= ... .desc >> （直接输出英文 desc）")
print("=" * 95)
n = 0
for m in re.finditer(r"<<=\s*[^>]{0,80}\.desc\s*>>", g):
    n += 1
    if n <= 10:
        print(f"  @{m.start()}: {g[max(0,m.start()-150):m.start()+150]!r}")
print(f"  共 {n} 处")

print("\n" + "=" * 95)
print("3. <<print ... .desc >>")
print("=" * 95)
n2 = 0
for m in re.finditer(r"<<print\s+[^>]{0,100}\.desc\s*>>", g):
    n2 += 1
    if n2 <= 10:
        print(f"  @{m.start()}: {g[max(0,m.start()-150):m.start()+150]!r}")
print(f"  共 {n2} 处")

print("\n" + "=" * 95)
print("4. $NPCList[...].desc 直接出现在正文里")
print("=" * 95)
n3 = 0
for m in re.finditer(r"\$NPCList\[[^\]]{1,40}\]\.desc(?!CN)", g):
    n3 += 1
    if n3 <= 15:
        ctx = g[max(0, m.start() - 120):m.start() + 150]
        print(f"  @{m.start()}: {ctx!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("5. _desc_CN 数组的读取位置")
print("=" * 95)
for m in list(re.finditer(r"_desc_CN", g))[:10]:
    print(f"  @{m.start()}: {g[max(0,m.start()-150):m.start()+200]!r}")
    print()
