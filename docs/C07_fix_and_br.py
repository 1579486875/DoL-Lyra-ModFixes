"""C07：修「且」运算符 + 查 <<br>> 的各种变体。"""
import html as H
import os
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r"<tw-passagedata", data)) < 10000:
    print("❌ index 不是明文形态")
    raise SystemExit(1)

print("=" * 90)
print("1) 修「且」运算符")
print("=" * 90)
n = 0
for old, new in [
    ("<<if $audience gte 0 且 $audience lte 5>>",
     "<<if $audience gte 0 and $audience lte 5>>"),
]:
    if old in data:
        c = data.count(old)
        data = data.replace(old, new)
        n += c
        print(f"  ✅ {c} 处: {old!r}")

# 通用：<<if ... 中文运算符 ...>>
pat = re.compile(r'(<<if\b[^>]{0,400}?)\s+且\s+([^>]{0,400}?>>)')
c = len(pat.findall(data))
if c:
    data = pat.sub(r"\1 and \2", data)
    n += c
    print(f"  ✅ 通用替换「且」-> and: {c} 处")

pat2 = re.compile(r'(<<if\b[^>]{0,400}?)\s+或\s+([^>]{0,400}?>>)')
c = len(pat2.findall(data))
if c:
    data = pat2.sub(r"\1 or \2", data)
    n += c
    print(f"  ✅ 通用替换「或」-> or: {c} 处")

print("\n" + "=" * 90)
print("2) <<br>> 的各种变体")
print("=" * 90)
for pat_str, label in [
    (r"<<br\s*>>", "<<br>>"),
    (r"<<br\s*/?>>", "<<br />>"),
    (r"&lt;&lt;br", "&lt;&lt;br"),
    (r"<br\s*/>", "<br />"),
]:
    hs = list(re.finditer(pat_str, data))
    print(f"  {label}: {len(hs)} 处")
    for m in hs[:3]:
        print(f"    @{m.start()}: {data[max(0,m.start()-80):m.start()+80]!r}")

print("\n" + "=" * 90)
print("3) 查 danceaudience widget 里有没有中文")
print("=" * 90)
m = re.search(r'<<widget "danceaudience">>(.*?)<</widget>>', data, re.S)
if m:
    body = m.group(1)
    print(f"  widget 长度 {len(body)}")
    cn = re.findall(r'<<if\b[^>]*[\u4e00-\u9fff][^>]*>>', body)
    print(f"  含中文的 <<if>>: {len(cn)}")
    for x in cn[:5]:
        print(f"    {x!r}")

if n:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n✅ 共修 {n} 处")

# 校验
g = open(HTML, "rb").read().decode("utf-8", "replace")
print("\n" + "=" * 90)
print("4) 校验")
print("=" * 90)
print(f"  passage: {len(re.findall(r'<tw-passagedata', g))}")
for kw in ["且 $audience", "或 $audience"]:
    print(f"  {kw!r}: {g.count(kw)}")
cn_if = re.findall(r'<<if\b[^>]*[\u4e00-\u9fff][^>]*>>', g)
print(f"  含中文的 <<if>> 总数: {len(cn_if)}（大部分是字符串参数，正常）")
