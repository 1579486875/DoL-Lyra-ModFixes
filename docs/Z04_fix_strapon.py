"""Z04：修 straponGeneratorOptions 的英文尺寸选项（幂等）。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[Z04] index 形态异常")
    sys.exit(1)

MARK = "[Z04]"
g0 = H.unescape(data)
if MARK in g0:
    print("[Z04] 已存在，跳过")
    sys.exit(0)

# <<option "显示文本" 值>> —— 只翻显示文本，值不变
FIXES = [
    ('<<option "regular" 2>>', '<<option "普通" 2>>'),
    ('<<option "large" 3>>', '<<option "大" 3>>'),
    ('<<option "massive" 4>>', '<<option "巨大" 4>>'),
]

total = 0
print("=" * 90)
print("修复 straponGeneratorOptions")
print("=" * 90)
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    if hit:
        total += hit
        print(f"  OK {hit}x  {old!r}")
    else:
        print(f"  MISS     {old!r}")

data = data.replace(
    H.escape('<<widget "generateshoppage">>', quote=False),
    H.escape('<!-- [Z04] 假阳具尺寸选项翻译 -->' + '<<widget "generateshoppage">>', quote=False), 1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"\n共修 {total} 处")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
m = re.search(r'<<widget "straponGeneratorOptions">>(.{0,400})', g, re.S)
if m:
    print(m.group(1)[:400])
print(f"\n  <<option \"regular\" 2>> 残留: {g.count(chr(60)*2 + 'option ' + chr(34) + 'regular' + chr(34))}")
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if total == 3 else 1)
