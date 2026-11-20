"""N05：查 <<person>> 等显示 widget 用的是 description 还是 description_CN。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("=" * 95)
print("1. <<person>> widget 定义")
print("=" * 95)
for pname, body in PASSAGES.items():
    m = re.search(r'<<widget "person">>(.*?)<</widget>>', body, re.S)
    if m:
        print(f"  [{pname}]")
        print(f"  {m.group(1)[:1500]!r}")
        break

print("\n" + "=" * 95)
print("2. 所有 widget 里用 description（不带 _CN）的地方")
print("=" * 95)
n = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r"\.description(?!_CN)\b", body):
        ctx = body[max(0, m.start() - 80):m.start() + 100]
        # 排除 set 赋值
        if re.search(r"<<set[^>]*\.description\s+to", ctx):
            continue
        n += 1
        if n <= 20:
            print(f"  [{pname}] @{m.start()}: {ctx!r}")
print(f"  共 {n} 处（非赋值）")

print("\n" + "=" * 95)
print("3. <<= ... description >> 输出")
print("=" * 95)
for m in re.finditer(r"<<=\s*[^>]{0,100}\.description(?!_CN)\s*>>", g):
    print(f"  @{m.start()}: {g[max(0,m.start()-150):m.start()+150]!r}")

print("\n" + "=" * 95)
print("4. <<print ... description >> 输出")
print("=" * 95)
for m in re.finditer(r"<<print\s+[^>]{0,100}\.description(?!_CN)\s*>>", g):
    print(f"  @{m.start()}: {g[max(0,m.start()-150):m.start()+150]!r}")
