"""T24：修两个真问题（幂等）。
1. 三重尖括号 >>>（会多渲染一个 >）
2. setup.CafeFoodList_cn_name 两次赋值丢词 —— 合并
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[T24] index 形态异常")
    sys.exit(1)

MARK = "[T24]"
g0 = H.unescape(data)
if MARK in g0:
    print("[T24] 已存在，跳过")
    sys.exit(0)

total = 0
g = g0

print("=" * 90)
print("1. 合并 CafeFoodList_cn_name（两次赋值，后者覆盖前者）")
print("=" * 90)
ms = list(re.finditer(r'<<set\s+setup\.CafeFoodList_cn_name\s+to\s+"([^"]*)"', g))
print(f"  找到 {len(ms)} 次赋值")
if len(ms) == 2:
    a, b = ms[0].group(1), ms[1].group(1)

    def parse(s):
        d = {}
        for item in s.split("|"):
            if "," in item:
                k, v = item.split(",", 1)
                d[k.strip()] = v.strip()
        return d

    da, db = parse(a), parse(b)
    merged = dict(db)
    added = []
    for k, v in da.items():
        if k not in merged:
            merged[k] = v
            added.append(k)
    print(f"  第一份 {len(da)} 词 / 第二份 {len(db)} 词 / 合并后 {len(merged)} 词")
    print(f"  补回 {len(added)} 个: {added}")

    new_val = "|".join(f"{k},{v}" for k, v in merged.items())
    # 删掉第一次赋值，第二次改成合并值
    old1 = ms[0].group(0)
    old2 = ms[1].group(0)
    new2 = '<<set setup.CafeFoodList_cn_name to "' + new_val + '"'
    # 在 data 上操作
    for o, n in ((H.escape(old1, quote=False) + "\n", ""),
                 (H.escape(old1, quote=False), "")):
        if o in data:
            data = data.replace(o, "", 1)
            break
    for o, n in ((H.escape(old2, quote=False), H.escape(new2, quote=False)),
                 (old2, new2)):
        if o in data:
            data = data.replace(o, n, 1)
            break
    total += 2
    print("  ✅ 已合并")

print("\n" + "=" * 90)
print("2. 三重尖括号 >>>")
print("=" * 90)
# 只处理三种已知形态
TRIPLE = [
    ('<<tending 5>><</if>>>', '<<tending 5>><</if>>'),
    ('<<upperwear "oversized button-down" "white">>>', '<<upperwear "oversized button-down" "white">>'),
]
for old, new in TRIPLE:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {old[:60]!r}")
    else:
        print(f"  MISS     {old[:60]!r}")

# 打标记
data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [T24] ==== -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# ---- 校验 ----
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
cs = re.findall(r'<<set\s+setup\.CafeFoodList_cn_name\s+to\s+"([^"]*)"', g2)
print(f"  CafeFoodList 赋值次数: {len(cs)}")
if cs:
    items = [x for x in cs[0].split("|") if "," in x]
    print(f"  条目数: {len(items)}")
    for k in ("fruity ale", "autumn ale", "winter ale", "crepes", "gingerbread", "coffee", "tea"):
        print(f"    {'OK ' if k + ',' in cs[0] else 'MISS'} {k}")

n3 = len(re.findall(r">>>", g2))
print(f"\n  三重 >>> 残留: {n3}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
