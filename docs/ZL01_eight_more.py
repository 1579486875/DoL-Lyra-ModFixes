"""第 31-40 轮：最后 8 个维度。

G) <<for>> 循环变量作用域混用（$i vs _i）
H) <<nobr>> / <<silently>> / <<capture>> 配对
I) /* */ 与 /% %/ 注释配对
J) passage 名重复
K) <<include>> 循环引用
L) <<run>> 里的赋值副作用
M) setup 对象被整体替换
N) 字符串内未闭合引号（粗略）
"""
import html
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return html.unescape(raw), blocks, raw


mg, mb, mraw = load(APK)
vg, vb, vraw = load(VAN)

print("=" * 90)
print("G) <<for>> 循环变量用 $（存档变量）而非 _（临时）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    hits = re.findall(r"<<for\s+\$(\w+)\s", g)
    c = Counter(hits)
    print(f"  {label}: {len(hits)} 处，{len(c)} 种")
    for k, v in c.most_common(10):
        print(f"    ${k} × {v}")

print("\n" + "=" * 90)
print("H) <<nobr>> / <<silently>> / <<capture>> 配对")
print("=" * 90)
for tag, op, cp in [("nobr", r"<<nobr\b", "<</nobr>>"),
                    ("silently", r"<<silently\b", "<</silently>>"),
                    ("capture", r"<<capture\b", "<</capture>>")]:
    for label, g in (("modded", mg), ("vanilla", vg)):
        o = len(re.findall(op, g))
        c = g.count(cp)
        flag = "✅" if o == c else f"❌ 差 {o-c}"
        print(f"  <<{tag}>> {label}: {o}/{c}  {flag}")

print("\n" + "=" * 90)
print("I) 注释配对")
print("=" * 90)
for label, r in (("modded", mraw), ("vanilla", vraw)):
    a = r.count("&lt;!--")
    b = r.count("--&gt;")
    c1 = r.count("/*")
    c2 = r.count("*/")
    d1 = r.count("/%")
    d2 = r.count("%/")
    print(f"  {label}: <!-- {a}/{b}  /* {c1}/{c2}  /% {d1}/{d2}")

print("\n" + "=" * 90)
print("J) passage 名重复")
print("=" * 90)
for label, raw in (("modded", mraw), ("vanilla", vraw)):
    names = [html.unescape(m.group(1)) for m in
             re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"', raw)]
    dup = [k for k, v in Counter(names).items() if v > 1]
    print(f"  {label}: {len(names)} 个，重复 {len(dup)}  {dup[:5]}")

print("\n" + "=" * 90)
print("K) <<include>> 循环引用（A include B 且 B include A）")
print("=" * 90)


def inc_map(blocks):
    out = defaultdict(set)
    for pn, b in blocks.items():
        for m in re.finditer(r'<<include\s+"([^"]+)"', b):
            out[pn].add(m.group(1))
    return out


im = inc_map(mb)
cycles = []
for a, bs in im.items():
    for b in bs:
        if b in im and a in im[b] and a != b:
            cycles.append((a, b))
print(f"  直接双向往返: {len(cycles)} 对")
for a, b in cycles[:10]:
    print(f"    {a} <-> {b}")

print("\n" + "=" * 90)
print("L) <<run>> 里的赋值（可能改坏状态）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    runs = re.findall(r"<<run\s+([^>]{1,200})>>", g)
    assign = [r for r in runs if re.search(r"\$[\w.]+\s*=[^=]", r)]
    print(f"  {label}: <<run>> {len(runs)} 处，含赋值 {len(assign)} 处")
    for a in assign[:5]:
        print(f"    {a[:100]!r}")

print("\n" + "=" * 90)
print("M) setup 对象被整体替换")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    n = len(re.findall(r"<<set\s+setup\s*to\s", g))
    print(f"  {label}: {n} 处")

print("\n" + "=" * 90)
print("N) <<if>> 里未闭合引号（粗略）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    bad = 0
    for m in re.finditer(r"<<(?:if|elseif|unless|while)\s+([^>]{1,300})>>", g):
        e = m.group(1)
        for q in ('"', "'"):
            cleaned = re.sub(r"\\" + q, "", e)
            if cleaned.count(q) % 2:
                bad += 1
                break
    print(f"  {label}: {bad} 处")
